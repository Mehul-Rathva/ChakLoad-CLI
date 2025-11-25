"""UI components using Rich library."""
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.theme import Theme
from loadtester.utils.logger import logger
import time

# Define color themes
THEMES = {
    "gemini": {
        "primary": "#32B8C6",
        "success": "#22C55E",
        "error": "#EF4444",
        "warning": "#F59E0B",
        "info": "#3B82F6",
        "background": "#1F2121",
        "foreground": "#F5F5F5",
    },
    "qwen": {
        "primary": "#7C3AED",
        "success": "#10B981",
        "error": "#DC2626",
        "warning": "#FBBF24",
        "info": "#06B6D4",
        "background": "#0F172A",
        "foreground": "#E2E8F0",
    },
    "ocean": {
        "primary": "#0EA5E9",
        "success": "#14B8A6",
        "error": "#F43F5E",
        "warning": "#FB923C",
        "info": "#8B5CF6",
        "background": "#0C4A6E",
        "foreground": "#F0F9FF",
    },
    "terminal": {
        "primary": "#00FF00",
        "success": "#00FF00",
        "error": "#FF0000",
        "warning": "#FFFF00",
        "info": "#00FFFF",
        "background": "#000000",
        "foreground": "#00FF00",
    }
}

# Initialize console with custom theme
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "accent": "#32B8C6",
    "highlight": "bold white on #32B8C6"
})

console = Console(theme=custom_theme)

def show_welcome_screen():
    """Display the welcome screen."""
    welcome_text = Text.from_markup(
        "[bold #32B8C6]🚀 LoadTester CLI[/bold #32B8C6]\n\n"
        "[#7C3AED]Comprehensive load testing tool with support for multiple frameworks[/#7C3AED]\n"
        "[#7C3AED]Locust, K6, Artillery, JMeter[/#7C3AED]\n\n"
        "[bold]Type /help for available commands[/bold]"
    )
    
    panel = Panel(
        welcome_text,
        title="[bold #32B8C6]Welcome to LoadTester CLI[/bold #32B8C6]",
        border_style="#32B8C6",
        padding=(1, 2),
        expand=False
    )
    
    console.print(panel)

def show_framework_menu():
    """Display framework selection menu."""
    table = Table(title="🔧 Select Testing Framework", border_style="#32B8C6")
    table.add_column("Framework", style="#32B8C6", no_wrap=True)
    table.add_column("Description", style="dim")
    
    table.add_row("Locust", "[green]Python-based, easy to use with Python scripting[/green]")
    table.add_row("K6", "[cyan]Go-based, high-performance with JavaScript[/cyan]")
    table.add_row("Artillery", "[yellow]Node.js, YAML configuration[/yellow]")
    table.add_row("JMeter", "[magenta]Java-based, enterprise features[/magenta]")
    
    console.print(table)
    
    console.print("\n[bold]Usage:[/bold] /framework [framework_name]")

def show_test_type_menu():
    """Display test type selection menu."""
    table = Table(title="🧪 Select Test Type", border_style="#32B8C6")
    table.add_column("Type", style="#32B8C6", no_wrap=True)
    table.add_column("Description", style="dim")
    
    table.add_row("web-site", "Test website (HTTP/HTTPS requests)")
    table.add_row("telegram-webhook", "Test Telegram Bot webhook")
    table.add_row("api-endpoint", "Test REST API endpoint")
    table.add_row("graphql", "Test GraphQL endpoint")
    table.add_row("websocket", "Test WebSocket connections")
    
    console.print(table)
    
    console.print("\n[bold]Usage:[/bold] /type [test_type]")

def show_config_summary(config):
    """Display current configuration."""
    config_text = (
        f"[bold]🎯 URL:[/bold] {config.target_url}\n"
        f"[bold]👥 Users:[/bold] {config.users}\n"
        f"[bold]⏱️ Duration:[/bold] {config.duration}s\n"
        f"[bold]📈 Ramp-up:[/bold] {config.rampup}s\n"
        f"[bold]🧪 Test Type:[/bold] {config.test_type}\n"
        f"[bold]⚙️ Framework:[/bold] {config.framework}"
    )
    
    panel = Panel(
        config_text,
        title="[bold #32B8C6]⚙️ Current Configuration[/bold #32B8C6]",
        border_style="#32B8C6",
        padding=(1, 2)
    )
    
    console.print(panel)

def show_progress(status_msg: str = "Running test..."):
    """Display progress during test execution."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task(status_msg, total=100)
        
        # Simulate progress for demo purposes
        for i in range(100):
            time.sleep(0.1)  # Simulate work
            progress.update(task, advance=1)

def show_results_summary(results):
    """Display test results summary."""
    results_text = (
        f"[bold]📊 Total Requests:[/bold] {results.total_requests}\n"
        f"[bold]✅ Successful:[/bold] {results.successful_requests}\n"
        f"[bold]❌ Failed:[/bold] {results.failed_requests}\n"
        f"[bold]📈 RPS (Requests/sec):[/bold] {results.requests_per_second}\n"
        f"[bold]⏱️ Avg Response Time:[/bold] {results.avg_response_time}ms\n"
        f"[bold]⚠️ Error Rate:[/bold] {results.error_rate}%"
    )
    
    panel = Panel(
        results_text,
        title="[bold #32B8C6]✅ Test Results[/bold #32B8C6]",
        border_style="#32B8C6",
        padding=(1, 2)
    )
    
    console.print(panel)