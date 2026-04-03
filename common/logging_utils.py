import logging
import json
import uuid
import sys
from datetime import datetime
from contextvars import ContextVar

# Context variable for correlation ID
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default=str(uuid.uuid4()))

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "line": record.lineno,
            "correlation_id": correlation_id_ctx.get(),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logging(service_name: str):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    
    logger.handlers = [handler]
    return logging.getLogger(service_name)

def get_logger(name: str):
    return logging.getLogger(name)
