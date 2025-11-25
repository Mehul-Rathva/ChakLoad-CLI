"""Logging utilities for the loadtester CLI."""
from loguru import logger
import sys

# Remove default logger to avoid duplicate messages
logger.remove()

# Add custom logger with rich formatting
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# Optionally add file logging
# logger.add("logs/loadtester.log", rotation="10 MB", level="DEBUG")