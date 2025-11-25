"""Progress and status UI components."""
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, TaskProgressColumn
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import Optional

from loadtester.frameworks.base import TestResults

console = Console()

def show_test_progress(config) -> Progress:
    """Create and return a progress bar for the test."""
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
        transient=True
    )

    return progress

def create_realtime_metrics_panel(
    active_users: int = 0,
    requests_made: int = 0,
    rps: float = 0.0,
    avg_response: float = 0.0,
    error_rate: float = 0.0
):
    """Create a panel showing real-time metrics during the test."""
    metrics_text = (
        f"Active Users: [bold]{active_users}[/bold]\n"
        f"Requests: [bold]{requests_made:,}[/bold]\n"
        f"RPS: [bold]{rps:.1f}[/bold]\n"
        f"Avg. Response: [bold]{avg_response:.1f}ms[/bold]\n"
        f"Error Rate: [bold]{error_rate:.1f}%[/bold]"
    )
    
    panel = Panel(
        metrics_text,
        title="Real-time Metrics",
        border_style="cyan",
        padding=(1, 2)
    )
    
    return panel

def display_final_results(results: TestResults):
    """Display the final test results in a formatted table."""
    # Main summary table
    summary_table = Table(title="📊 Final Test Results", border_style="green")
    summary_table.add_column("Metric", style="bold")
    summary_table.add_column("Value", justify="right")
    
    summary_table.add_row("Total Requests", f"{results.total_requests:,}")
    summary_table.add_row("Successful Requests", f"{results.successful_requests:,}")
    summary_table.add_row("Failed Requests", f"{results.failed_requests:,}")
    summary_table.add_row("Requests per Second", f"{results.requests_per_second:.2f}")
    summary_table.add_row("Success Rate", f"{(results.successful_requests/results.total_requests*100):.2f}%" if results.total_requests > 0 else "0%")
    
    # Response time table
    response_table = Table(title="⏱️ Response Times", border_style="blue")
    response_table.add_column("Metric", style="bold")
    response_table.add_column("Value (ms)", justify="right")
    
    response_table.add_row("Average", f"{results.avg_response_time:.2f}")
    response_table.add_row("Median", f"{results.median_response_time:.2f}")
    response_table.add_row("Min", f"{results.min_response_time:.2f}")
    response_table.add_row("Max", f"{results.max_response_time:.2f}")
    response_table.add_row("95th Percentile", f"{results.p95_response_time:.2f}")
    response_table.add_row("99th Percentile", f"{results.p99_response_time:.2f}")
    
    # Error table if there are errors
    error_table = None
    if results.errors and len(results.errors) > 0:
        error_table = Table(title="❌ Errors", border_style="red")
        error_table.add_column("Error Type", style="bold")
        error_table.add_column("Count", justify="right")
        error_table.add_column("Percentage", justify="right")
        
        total_errors = sum(results.errors.values())
        for error_type, count in results.errors.items():
            percentage = (count / results.total_requests) * 100 if results.total_requests > 0 else 0
            error_table.add_row(error_type, str(count), f"{percentage:.2f}%")
    
    # Network statistics
    network_table = Table(title="🌐 Network Statistics", border_style="magenta")
    network_table.add_column("Metric", style="bold")
    network_table.add_column("Value", justify="right")
    
    network_table.add_row("Data Sent", f"{results.data_sent_mb:.2f} MB")
    network_table.add_row("Data Received", f"{results.data_received_mb:.2f} MB")
    network_table.add_row("Duration", f"{results.duration}s")
    network_table.add_row("Error Rate", f"{results.error_rate:.2f}%")
    
    console.print(summary_table)
    console.print(response_table)
    if error_table:
        console.print(error_table)
    console.print(network_table)

def show_loading_animation(message: str = "Processing..."):
    """Show a simple loading animation."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(message, total=None)
        
        # In a real implementation, this would be updated based on actual processing
        # For now, just show the spinner
        import time
        time.sleep(2)  # Simulate processing time