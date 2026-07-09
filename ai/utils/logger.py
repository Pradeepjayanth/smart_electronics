import logging
import os

def get_logger(name, log_file="ai_pipeline.log"):
    """
    Creates and configures a standard logger.
    
    Args:
        name (str): Name of the module.
        log_file (str): Filename for the log output.
        
    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(name)
    
    # Avoid adding duplicate handlers if logger already exists
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Determine logs directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.abspath(os.path.join(script_dir, "../logs"))
        os.makedirs(logs_dir, exist_ok=True)
        
        log_path = os.path.join(logs_dir, log_file)
        
        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(log_path)
        
        c_handler.setLevel(logging.INFO)
        f_handler.setLevel(logging.DEBUG)
        
        # Create formatters and add it to handlers
        c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)
        
        # Add handlers to the logger
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)
        
    return logger
