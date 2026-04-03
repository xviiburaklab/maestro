import logging
from common.events import EventConsumer
from worker.tasks import execute_workflow
from common.logging_utils import setup_logging

logger = setup_logging("worker")

if __name__ == "__main__":
    consumer = EventConsumer(queue_name="workflow_queue", topic_pattern="workflow.*")
    logger.info("Worker started, waiting for workflow events...")
    consumer.consume(execute_workflow)
