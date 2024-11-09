import logging

# Configure logging
logging.basicConfig(
    level=logging.WARNING,  # Set the logging level to WARNING
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Output logs to the console
    ]
)

# Create a logger for the application
logger = logging.getLogger('nihilis')