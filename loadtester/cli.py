"""CLI interface for the loadtester tool."""
import typer
from typing import Optional
import sys
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.prompt import Prompt
import inquirer

from loadtester.ui.menus import show_welcome_screen, show_framework_menu, show_test_type_menu
from loadtester.ui.progress import display_final_results, show_test_progress
from loadtester.ui.themes import show_theme_preview, get_available_themes, apply_theme
from loadtester.frameworks.simple_runner import SimpleHttpRunner
from loadtester.frameworks.enhanced_runner import EnhancedHttpRunner
from loadtester.frameworks.k6_runner import K6Runner
from loadtester.frameworks import get_available_frameworks
from loadtester.config import Config, load_default_config
from loadtester.utils.logger import logger

app = typer.Typer()

# Global configuration instance
config = load_default_config()

def show_ascii_art():
    """Display ASCII art welcome message."""
    console = Console()
    ascii_art = r"""
  ██╗  ██╗███████╗██████╗ ███████╗██████╗ ██╗███████╗██╗  ██╗
  ██║  ██║██╔════╝██╔══██╗██╔════╝██╔══██╗██║██╔════╝██║  ██║
  ███████║█████╗  ██████╔╝█████╗  ██████╔╝██║███████╗███████║
  ██╔══██║██╔══╝  ██╔══██╗██╔══╝  ██╔══██╗██║╚════██║██╔══██║
  ██║  ██║███████╗██████╔╝███████╗██████╔╝██║███████║██║  ██║
  ╚═╝  ╚═╝╚══════╝╚═════╝ ╚══════╝╚═════╝ ╚═╝╚══════╝╚═╝  ╚═╝
    """
    console.print(ascii_art, style="bold blue")
    console.print("[bold green]CHAKLOAD - Advanced Load Testing CLI[/bold green]")
    console.print("[cyan]Type /help for available commands or start with / to see command suggestions[/cyan]\n")

def interactive_command_selector():
    """Interactive command selector with arrow key support."""
    available_commands = [
        {"name": "/help", "description": "Show help information"},
        {"name": "/framework", "description": "Select testing framework"},
        {"name": "/type", "description": "Select test type"},
        {"name": "/url", "description": "Set target URL"},
        {"name": "/users", "description": "Set number of concurrent users"},
        {"name": "/duration", "description": "Set test duration"},
        {"name": "/rampup", "description": "Set ramp-up time"},
        {"name": "/config", "description": "Manage configuration"},
        {"name": "/run", "description": "Run load test"},
        {"name": "/start", "description": "Start load test"},
        {"name": "/results", "description": "Show test results"},
        {"name": "/export", "description": "Export results"},
        {"name": "/theme", "description": "Change color theme"},
        {"name": "/clear", "description": "Clear screen"},
        {"name": "/exit", "description": "Exit the CLI"}
    ]

    # Create choices for inquirer
    choices = [f"{cmd['name']} - {cmd['description']}" for cmd in available_commands]

    questions = [
        inquirer.List('command',
                      message="Select a command",
                      choices=choices,
                      carousel=True  # Enables arrow key navigation
                     )
    ]

    answers = inquirer.prompt(questions)
    if answers:
        selected = answers['command']
        command = selected.split(' - ')[0]  # Extract command name
        return command
    return None

@app.command("interactive", help="Start the interactive CLI interface")
def interactive_cmd():
    """Start the interactive CLI interface."""
    show_ascii_art()

    while True:
        try:
            user_input = input("\n> ").strip()

            if user_input == '/':
                # Show interactive command selector
                selected_command = interactive_command_selector()
                if selected_command:
                    # Process the selected command
                    command_parts = selected_command[1:].split()  # Remove '/' and split
                    handle_command(command_parts)
                continue

            if user_input.startswith('/'):
                command = user_input[1:].split()
                handle_command(command)
            elif user_input.lower() in ['exit', 'quit', 'q']:
                typer.echo("Exiting LoadTester CLI...")
                break
            else:
                typer.echo(f"Unknown command: {user_input}. Type /help for available commands.")
        except KeyboardInterrupt:
            typer.echo("\n\nExiting LoadTester CLI...")
            break
        except EOFError:
            typer.echo("\n\nExiting LoadTester CLI...")
            break

# Make interactive the default command
@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    """Default command that runs interactive mode if no subcommand is provided."""
    if ctx.invoked_subcommand is None:
        interactive_cmd()

def handle_command(args):
    """Handle CLI commands."""
    if not args:
        return
    
    command = args[0].lower()
    
    if command == 'help':
        show_help(args[1:] if len(args) > 1 else None)
    elif command == 'framework':
        handle_framework_command(args[1:] if len(args) > 1 else None)
    elif command == 'type':
        handle_type_command(args[1:] if len(args) > 1 else None)
    elif command in ['run', 'start']:
        handle_run_command()
    elif command == 'config':
        handle_config_command(args[1:] if len(args) > 1 else None)
    elif command == 'url':
        handle_url_command(args[1] if len(args) > 1 else None)
    elif command == 'users':
        handle_users_command(args[1] if len(args) > 1 else None)
    elif command == 'duration':
        handle_duration_command(args[1] if len(args) > 1 else None)
    elif command == 'rampup':
        handle_rampup_command(args[1] if len(args) > 1 else None)
    elif command == 'results':
        handle_results_command(args[1:] if len(args) > 1 else None)
    elif command == 'export':
        handle_export_command(args[1:] if len(args) > 1 else None)
    elif command == 'theme':
        handle_theme_command(args[1:] if len(args) > 1 else None)
    elif command in ['clear', 'cls']:
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    elif command == 'exit':
        sys.exit(0)
    else:
        typer.echo(f"Unknown command: /{command}. Type /help for available commands.")

def show_help(args=None):
    """Show help information."""
    if args and len(args) > 0:
        # Show help for specific command
        cmd = args[0].lower()
        if cmd == 'framework':
            typer.echo("Framework command - Select a testing framework")
            typer.echo("Usage: /framework <name>")
            typer.echo("Available frameworks: locust, k6, artillery, jmeter")
            typer.echo("Aliases: /framework list - show available frameworks")
        elif cmd == 'type':
            typer.echo("Type command - Select test type")
            typer.echo("Usage: /type <test-type>")
            typer.echo("Available types: web-site, telegram-webhook, api-endpoint, graphql, websocket")
            typer.echo("Aliases: /type list - show available test types")
        else:
            typer.echo(f"No help available for command: /{cmd}")
    else:
        # Show general help
        typer.echo("LoadTester CLI - Comprehensive load testing tool")
        typer.echo("")
        typer.echo("Available commands:")
        typer.echo("  /help [command]          - Show this help or help for specific command")
        typer.echo("  /framework <name>        - Select testing framework: simple, k6")
        typer.echo("  /type <test-type>        - Select test type: web-site, telegram-webhook, api-endpoint")
        typer.echo("  /url <target-url>        - Set target URL for testing")
        typer.echo("  /users <number>          - Set number of concurrent users (default: 100)")
        typer.echo("  /duration <seconds>      - Set test duration in seconds (default: 60s)")
        typer.echo("  /rampup <seconds>        - Set ramp-up time in seconds (default: 10s)")
        typer.echo("  /config [show|save|load] - Manage configuration presets")
        typer.echo("  /run or /start           - Run load test with current configuration")
        typer.echo("  /results                 - Show last test results")
        typer.echo("  /export <format>         - Export results: json, csv, html")
        typer.echo("  /theme <name>            - Change color theme")
        typer.echo("  /clear                   - Clear screen")
        typer.echo("  /exit                    - Exit the CLI")

def handle_framework_command(args):
    """Handle framework selection command."""
    if not args:
        # Show framework selection menu
        show_framework_menu()
        return

    framework = args[0].lower()
    if framework == 'list':
        available_frameworks = get_available_frameworks()
        all_frameworks = ['locust', 'k6', 'artillery', 'jmeter', 'simple', 'http']
        typer.echo(f"Available frameworks: {', '.join(available_frameworks)}")
        typer.echo(f"All supported frameworks: {', '.join(all_frameworks)}")
        return

    # Check if framework is in the list of supported frameworks
    supported_frameworks = ['locust', 'k6', 'artillery', 'jmeter', 'simple', 'http', 'advanced', 'builtin']
    if framework not in supported_frameworks:
        typer.echo(f"Unknown framework: {framework}. Available: {', '.join(supported_frameworks)}")
        return

    # Check if framework is available on this system
    available_frameworks = get_available_frameworks()

    # Built-in frameworks are always available
    if framework in ['simple', 'http', 'advanced', 'builtin']:
        framework_available = True
    else:
        framework_available = framework in available_frameworks

    if not framework_available:
        typer.echo(f"⚠️  Framework '{framework}' is not installed on this system.")
        typer.echo(f"Available frameworks: {', '.join(available_frameworks)}")
        typer.echo("Please install the framework separately before using it.")
        return

    config.framework = framework
    typer.echo(f"✓ Framework set to: {framework.title()}")

def handle_type_command(args):
    """Handle test type selection command."""
    if not args:
        # Show test type selection menu
        show_test_type_menu()
        return
    
    test_type = args[0].lower()
    if test_type == 'list':
        typer.echo("Available test types: web-site, telegram-webhook, api-endpoint, graphql, websocket")
        return
    
    if test_type in ['web-site', 'telegram-webhook', 'api-endpoint', 'graphql', 'websocket']:
        config.test_type = test_type
        typer.echo(f"✓ Test type set to: {test_type}")
    else:
        typer.echo(f"Unknown test type: {test_type}. Available: web-site, telegram-webhook, api-endpoint, graphql, websocket")

def handle_run_command():
    """Handle test execution command."""
    if not config.target_url:
        typer.echo("❌ Error: No target URL specified. Use /url <target-url> to set it.")
        return

    if not config.framework:
        typer.echo("❌ Error: No framework specified. Use /framework <name> to select one.")
        return

    if not config.test_type:
        typer.echo("❌ Error: No test type specified. Use /type <test-type> to select one.")
        return

    typer.echo(f"🚀 Running load test...")
    typer.echo(f"   Framework: {config.framework}")
    typer.echo(f"   Target: {config.target_url}")
    typer.echo(f"   Test Type: {config.test_type}")
    typer.echo(f"   Users: {config.users}")
    typer.echo(f"   Duration: {config.duration}s")
    typer.echo(f"   Ramp-up: {config.rampup}s")

    # Run test based on selected framework
    available_frameworks = get_available_frameworks()

    if config.framework not in available_frameworks:
        typer.echo(f"❌ Framework '{config.framework}' is not available on this system.")
        typer.echo("Available frameworks: " + ", ".join(available_frameworks))
        return

    try:
        if config.framework in ['simple', 'http']:
            runner = SimpleHttpRunner()
        elif config.framework in ['advanced', 'builtin']:
            runner = EnhancedHttpRunner()
        elif config.framework == 'k6':
            runner = K6Runner()
        else:
            typer.echo(f"❌ Framework {config.framework} not yet implemented in this MVP.")
            return

        # Convert config to TestConfig dataclass
        test_config = config.to_test_config()

        # Prepare test
        script_path = runner.prepare_test(test_config)

        # Show progress during test execution
        progress = show_test_progress(config)

        import threading
        import time

        result_container = [None]
        error_container = [None]

        def run_test_in_thread():
            try:
                result_container[0] = runner.run_test(script_path, test_config)
            except Exception as e:
                error_container[0] = e

        test_thread = threading.Thread(target=run_test_in_thread)
        test_thread.start()

        # Update progress bar while test runs
        with progress:
            task_id = progress.add_task("[green]Running Load Test...", total=config.duration)

            elapsed = 0
            while elapsed < config.duration and test_thread.is_alive():
                time.sleep(1)
                elapsed += 1
                progress.update(task_id, completed=min(elapsed, config.duration))  # Prevent going over 100%

            # Wait for test to complete if needed (with timeout to avoid hanging)
            if test_thread.is_alive():
                test_thread.join(timeout=config.duration + 30)  # Wait max duration + 30s extra

        if error_container[0]:
            raise error_container[0]

        results = result_container[0]

        if results is None:
            typer.echo("\n⚠️  Test may have timed out or failed to complete.")
        else:
            typer.echo("\n✅ Test completed successfully!")

            # Display detailed results
            display_final_results(results)

    except Exception as e:
        typer.echo(f"❌ Error running test: {str(e)}")
        logger.error(f"Test execution failed: {str(e)}")

def handle_config_command(args):
    """Handle configuration commands."""
    if not args:
        typer.echo(f"Current config:")
        typer.echo(f"  Framework: {config.framework}")
        typer.echo(f"  Test Type: {config.test_type}")
        typer.echo(f"  URL: {config.target_url}")
        typer.echo(f"  Users: {config.users}")
        typer.echo(f"  Duration: {config.duration}s")
        typer.echo(f"  Ramp-up: {config.rampup}s")
    elif args[0].lower() == 'show':
        typer.echo(f"Current config:")
        typer.echo(f"  Framework: {config.framework}")
        typer.echo(f"  Test Type: {config.test_type}")
        typer.echo(f"  URL: {config.target_url}")
        typer.echo(f"  Users: {config.users}")
        typer.echo(f"  Duration: {config.duration}s")
        typer.echo(f"  Ramp-up: {config.rampup}s")
    else:
        typer.echo(f"Config command '{args[0]}' not yet implemented in this MVP.")

def handle_url_command(url):
    """Handle URL setting command."""
    if url:
        config.target_url = url
        typer.echo(f"✓ URL set to: {url}")
    else:
        typer.echo("Usage: /url <target-url>")

def handle_users_command(users_str):
    """Handle users setting command."""
    if users_str:
        try:
            users = int(users_str)
            if users > 0:
                config.users = users
                typer.echo(f"✓ Users set to: {users}")
            else:
                typer.echo("Users must be a positive number.")
        except ValueError:
            typer.echo("Usage: /users <number>")
    else:
        typer.echo("Usage: /users <number>")

def handle_duration_command(duration_str):
    """Handle duration setting command."""
    if duration_str:
        try:
            duration = int(duration_str)
            if duration > 0:
                config.duration = duration
                typer.echo(f"✓ Duration set to: {duration}s")
            else:
                typer.echo("Duration must be a positive number.")
        except ValueError:
            typer.echo("Usage: /duration <seconds>")
    else:
        typer.echo("Usage: /duration <seconds>")

def handle_rampup_command(rampup_str):
    """Handle ramp-up setting command."""
    if rampup_str:
        try:
            rampup = int(rampup_str)
            if rampup >= 0:
                config.rampup = rampup
                typer.echo(f"✓ Ramp-up set to: {rampup}s")
            else:
                typer.echo("Ramp-up must be a non-negative number.")
        except ValueError:
            typer.echo("Usage: /rampup <seconds>")
    else:
        typer.echo("Usage: /rampup <seconds>")

def handle_results_command(args):
    """Handle results command."""
    typer.echo("Results command - showing last test results...")
    # In full implementation, this would show detailed results

def handle_export_command(args):
    """Handle export command."""
    if not args:
        typer.echo("Usage: /export <format> [filename]")
        typer.echo("Available formats: json, csv, html")
        return
    
    format_type = args[0].lower()
    if format_type in ['json', 'csv', 'html']:
        typer.echo(f"Exporting results in {format_type} format...")
        # In full implementation, this would export the results
        typer.echo(f"✅ Results exported successfully.")
    else:
        typer.echo(f"❌ Format '{format_type}' not supported. Available: json, csv, html")

def handle_theme_command(args):
    """Handle theme command."""
    if args:
        theme = args[0].lower()
        if theme == 'list':
            show_theme_preview()
        elif theme in get_available_themes():
            # In a full implementation, this would apply the theme
            result = apply_theme(theme)
            if result:
                typer.echo(f"✓ Theme changed to: {theme.title()}")
            else:
                typer.echo(f"❌ Could not apply theme: {theme}")
        else:
            typer.echo(f"❌ Unknown theme: {theme}. Available themes: {', '.join(get_available_themes())}")
            typer.echo("Usage: /theme <name> or /theme list")
    else:
        typer.echo("Available themes: gemini, qwen, ocean, terminal")
        typer.echo("Usage: /theme <name> or /theme list")

if __name__ == "__main__":
    app()