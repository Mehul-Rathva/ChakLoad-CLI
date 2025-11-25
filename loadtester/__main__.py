"""Main entry point for the loadtester CLI."""
import sys
from loadtester.cli import app

def main():
    """Run the CLI application."""
    # If no arguments provided, typer will use the default callback
    app()

if __name__ == "__main__":
    main()