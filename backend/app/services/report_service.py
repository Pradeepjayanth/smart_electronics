"""
Report Service
==============

Service for generating comprehensive operational reports across multiple timeframes
(Daily, Weekly, Monthly, Yearly) and exporting them to JSON, CSV, and PDF formats.
"""

import csv
import io
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from motor.motor_asyncio import AsyncIOMotorDatabase
from app.utils.logger import logger


class ReportService:
    """Handles data compilation and multi-format exporting for Advanced Reports."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.devices = db.devices
        self.predictions = db.predictions
        self.sensor_data = db.sensor_data

    async def generate_summary_data(self, period: str = "daily") -> Dict[str, Any]:
        """
        Aggregate comprehensive summary metrics for the requested timeframe.

        Args:
            period: 'daily', 'weekly', 'monthly', or 'yearly'.

        Returns:
            Dict containing Failure Summary, Maintenance Summary, Warranty Summary,
            and Top Risk Devices.
        """
        now = datetime.now(timezone.utc)
        days_map = {"daily": 1, "weekly": 7, "monthly": 30, "yearly": 365}
        days = days_map.get(period.lower(), 1)
        start_date = now - timedelta(days=days)

        # 1. Failure Summary
        pred_pipeline = [
            {"$match": {"created_at": {"$gte": start_date}}},
            {
                "$group": {
                    "_id": None,
                    "total_predictions": {"$sum": 1},
                    "avg_failure_probability": {"$avg": "$failure_probability"},
                    "high_risk_count": {
                        "$sum": {"$cond": [{"$gte": ["$failure_probability", 0.5]}, 1, 0]}
                    },
                    "critical_count": {
                        "$sum": {"$cond": [{"$gte": ["$failure_probability", 0.75]}, 1, 0]}
                    }
                }
            }
        ]
        pred_cursor = self.predictions.aggregate(pred_pipeline)
        pred_res = await pred_cursor.to_list(length=1)
        failure_summary = pred_res[0] if pred_res else {
            "total_predictions": 0,
            "avg_failure_probability": 0.0,
            "high_risk_count": 0,
            "critical_count": 0
        }
        if "_id" in failure_summary:
            del failure_summary["_id"]

        # 2. Maintenance Summary
        device_status_pipeline = [
            {"$match": {"status": {"$ne": "inactive"}}},
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        status_cursor = self.devices.aggregate(device_status_pipeline)
        status_res = await status_cursor.to_list(length=10)
        maintenance_summary = {"active": 0, "warning": 0, "critical": 0, "maintenance": 0}
        for item in status_res:
            st = item["_id"]
            if st in maintenance_summary:
                maintenance_summary[st] = item["count"]

        # 3. Warranty Summary
        total_devices = await self.devices.count_documents({"status": {"$ne": "inactive"}})
        # Count warranties expiring within the next 30 days
        expiry_threshold = (now + timedelta(days=30)).isoformat()
        expiring_soon = await self.devices.count_documents({
            "status": {"$ne": "inactive"},
            "warranty_expiry": {"$lte": expiry_threshold, "$ne": None}
        })
        warranty_summary = {
            "total_monitored_devices": total_devices,
            "warranties_expiring_within_30_days": expiring_soon,
            "active_warranties": max(0, total_devices - expiring_soon)
        }

        # 4. Top Risk Devices
        top_risk_cursor = self.devices.find(
            {"status": {"$ne": "inactive"}},
            sort=[("health_score", 1)],
            limit=5
        )
        top_risk_devices = []
        async for doc in top_risk_cursor:
            top_risk_devices.append({
                "device_id": doc["device_id"],
                "name": doc.get("name", ""),
                "health_score": doc.get("health_score", 100.0),
                "status": doc.get("status", "active")
            })

        return {
            "report_period": period.upper(),
            "generated_at": now.isoformat(),
            "failure_summary": failure_summary,
            "maintenance_summary": maintenance_summary,
            "warranty_summary": warranty_summary,
            "top_risk_devices": top_risk_devices
        }

    @staticmethod
    def export_as_json(summary_data: Dict[str, Any]) -> str:
        """Serialize summary data into formatted JSON."""
        return json.dumps(summary_data, indent=2, default=str)

    @staticmethod
    def export_as_csv(summary_data: Dict[str, Any]) -> str:
        """Flatten summary data into a readable CSV string."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header info
        writer.writerow(["Smart Electronics Platform - Operational Report"])
        writer.writerow(["Period", summary_data.get("report_period", "N/A")])
        writer.writerow(["Generated At", summary_data.get("generated_at", "")])
        writer.writerow([])

        # Failure Summary
        writer.writerow(["=== FAILURE SUMMARY ==="])
        f_sum = summary_data.get("failure_summary", {})
        for k, v in f_sum.items():
            writer.writerow([k, v])
        writer.writerow([])

        # Maintenance Summary
        writer.writerow(["=== MAINTENANCE SUMMARY ==="])
        m_sum = summary_data.get("maintenance_summary", {})
        for k, v in m_sum.items():
            writer.writerow([k, v])
        writer.writerow([])

        # Warranty Summary
        writer.writerow(["=== WARRANTY SUMMARY ==="])
        w_sum = summary_data.get("warranty_summary", {})
        for k, v in w_sum.items():
            writer.writerow([k, v])
        writer.writerow([])

        # Top Risk Devices
        writer.writerow(["=== TOP RISK DEVICES ==="])
        writer.writerow(["Device ID", "Name", "Health Score", "Status"])
        for dev in summary_data.get("top_risk_devices", []):
            writer.writerow([
                dev.get("device_id"), dev.get("name"),
                dev.get("health_score"), dev.get("status")
            ])

        return output.getvalue()

    @staticmethod
    def export_as_pdf(summary_data: Dict[str, Any]) -> bytes:
        """
        Generate PDF report. Uses ReportLab if installed, otherwise creates a
        formatted text/HTML buffer disguised as readable report stream.
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Title
            title_style = styles["Title"]
            story.append(Paragraph(f"Operational Report ({summary_data.get('report_period')})", title_style))
            story.append(Spacer(1, 12))

            # Failure Summary Section
            story.append(Paragraph("<b>Failure Summary</b>", styles["Heading2"]))
            f_sum = summary_data.get("failure_summary", {})
            f_data = [[k, str(v)] for k, v in f_sum.items()]
            if f_data:
                t = Table(f_data, colWidths=[200, 200])
                t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
                story.append(t)
            story.append(Spacer(1, 12))

            # Top Risk Devices Table
            story.append(Paragraph("<b>Top Risk Devices</b>", styles["Heading2"]))
            devs = summary_data.get("top_risk_devices", [])
            if devs:
                dev_data = [["Device ID", "Name", "Health Score", "Status"]]
                for d in devs:
                    dev_data.append([str(d.get("device_id")), str(d.get("name")), str(d.get("health_score")), str(d.get("status"))])
                t2 = Table(dev_data, colWidths=[100, 150, 100, 100])
                t2.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
                ]))
                story.append(t2)

            doc.build(story)
            pdf_bytes = buffer.getvalue()
            buffer.close()
            return pdf_bytes

        except ImportError:
            logger.warning("ReportLab not installed. Generating text fallback for PDF stream.")
            # Fallback formatted bytes if reportlab is missing
            text_summary = ReportService.export_as_csv(summary_data)
            return text_summary.encode("utf-8")
