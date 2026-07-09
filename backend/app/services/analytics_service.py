"""
Analytics Service
=================

Executes MongoDB Aggregation Pipelines to surface deep prognostic insights,
trends, and averages across devices, sensor data, and prediction history.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from motor.motor_asyncio import AsyncIOMotorDatabase
from app.utils.logger import logger


class AnalyticsService:
    """Service for running analytical queries and aggregations over MongoDB."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.devices = db.devices
        self.sensor_data = db.sensor_data
        self.predictions = db.predictions

    async def get_averages(self) -> Dict[str, float]:
        """
        Compute average temperature, humidity, voltage, current, and health score
        across all recent readings and active devices.
        """
        # Average sensor metrics from sensor_data collection
        sensor_pipeline = [
            {
                "$group": {
                    "_id": None,
                    "avg_temperature": {"$avg": "$temperature"},
                    "avg_humidity": {"$avg": "$humidity"},
                    "avg_voltage": {"$avg": "$voltage"},
                    "avg_current": {"$avg": "$current"},
                }
            }
        ]
        sensor_cursor = self.sensor_data.aggregate(sensor_pipeline)
        sensor_result = await sensor_cursor.to_list(length=1)
        sensor_avgs = sensor_result[0] if sensor_result else {}

        # Average health score from active devices
        device_pipeline = [
            {"$match": {"status": {"$ne": "inactive"}}},
            {
                "$group": {
                    "_id": None,
                    "avg_health_score": {"$avg": "$health_score"}
                }
            }
        ]
        device_cursor = self.devices.aggregate(device_pipeline)
        device_result = await device_cursor.to_list(length=1)
        avg_health = device_result[0].get("avg_health_score", 100.0) if device_result else 100.0

        return {
            "average_temperature": round(sensor_avgs.get("avg_temperature", 0.0) or 0.0, 2),
            "average_humidity": round(sensor_avgs.get("avg_humidity", 0.0) or 0.0, 2),
            "average_voltage": round(sensor_avgs.get("avg_voltage", 0.0) or 0.0, 2),
            "average_current": round(sensor_avgs.get("avg_current", 0.0) or 0.0, 2),
            "average_health_score": round(avg_health or 100.0, 2),
        }

    async def get_risk_distribution(self) -> Dict[str, int]:
        """
        Count active devices broken down by their current risk/status tiers.
        Returns counts for low, medium, high, and critical.
        """
        pipeline = [
            {"$match": {"status": {"$ne": "inactive"}}},
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        cursor = self.devices.aggregate(pipeline)
        results = await cursor.to_list(length=10)

        # Map device status or risk tiers to counts
        distribution = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for item in results:
            status = item["_id"]
            count = item["count"]
            if status == "active":
                distribution["low"] += count
            elif status == "warning":
                distribution["medium"] += count
            elif status == "critical":
                distribution["critical"] += count
            elif status == "maintenance":
                distribution["high"] += count

        return distribution

    async def get_most_failed_devices(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve devices with the highest predicted failure probability or critical events.
        """
        pipeline = [
            {"$match": {"status": {"$ne": "inactive"}}},
            {"$sort": {"health_score": 1}},
            {"$limit": limit},
            {
                "$project": {
                    "_id": 0,
                    "device_id": 1,
                    "name": 1,
                    "health_score": 1,
                    "status": 1
                }
            }
        ]
        cursor = self.devices.aggregate(pipeline)
        return await cursor.to_list(length=limit)

    async def get_most_common_failure_causes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Identify the most frequent root causes from historical AI predictions.
        """
        pipeline = [
            {"$match": {"root_cause": {"$ne": "No significant anomalies detected"}}},
            {
                "$group": {
                    "_id": "$root_cause",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": limit},
            {
                "$project": {
                    "_id": 0,
                    "cause": "$_id",
                    "count": 1
                }
            }
        ]
        cursor = self.predictions.aggregate(pipeline)
        return await cursor.to_list(length=limit)

    async def get_trends(self, days: int = 7) -> Dict[str, List[Dict[str, Any]]]:
        """
        Compute daily failure trends and prediction volume over the past N days.
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        pipeline = [
            {"$match": {"created_at": {"$gte": cutoff_date}}},
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$created_at"},
                        "month": {"$month": "$created_at"},
                        "day": {"$dayOfMonth": "$created_at"}
                    },
                    "avg_failure_probability": {"$avg": "$failure_probability"},
                    "prediction_count": {"$sum": 1}
                }
            },
            {"$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}}
        ]
        cursor = self.predictions.aggregate(pipeline)
        results = await cursor.to_list(length=days + 1)

        failure_trend = []
        prediction_trend = []
        for item in results:
            date_str = f"{item['_id']['year']}-{item['_id']['month']:02d}-{item['_id']['day']:02d}"
            failure_trend.append({
                "date": date_str,
                "avg_failure_probability": round(item.get("avg_failure_probability", 0.0) or 0.0, 4)
            })
            prediction_trend.append({
                "date": date_str,
                "count": item["prediction_count"]
            })

        return {
            "failure_trend": failure_trend,
            "prediction_trend": prediction_trend,
        }
