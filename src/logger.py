import logging

def get_logger() -> logging.Logger:
    """Taken from
    https://www.crowdstrike.com/guides/python-logging/

    Returns:
        logging.Logger: _description_
    """
    logger = logging.getLogger('tutorial')

    # Set our log level
    logger.setLevel(logging.INFO)

    # create a console handler
    handler = logging.StreamHandler()
    
    # set INFO level for handler
    handler.setLevel(logging.INFO)

    # Create a message format we want for our logs
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Add our format to our handler
    handler.setFormatter(formatter)
    
    # Add our handler to our logger
    logger.addHandler(handler)
    
    #  Emit an INFO-level message
    logger.info('Python logging is up and running!')

    return logger