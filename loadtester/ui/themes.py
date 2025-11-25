"""Theme management for the CLI."""
from rich.console import Console
from rich.theme import Theme
from rich.table import Table

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

def get_available_themes():
    """Get list of available themes."""
    return list(THEMES.keys())

def show_theme_preview():
    """Show preview of all available themes."""
    table = Table(title="🎨 Available Themes", border_style="#32B8C6")
    table.add_column("Theme Name", style="#32B8C6", no_wrap=True)
    table.add_column("Primary Color", style="dim")
    table.add_column("Description", style="dim")
    
    theme_descriptions = {
        "gemini": "Modern teal theme with dark background",
        "qwen": "Purple theme with dark slate background",
        "ocean": "Ocean blue theme with deep blue background",
        "terminal": "Classic green terminal theme"
    }
    
    for theme_name, theme_colors in THEMES.items():
        description = theme_descriptions.get(theme_name, "No description")
        primary_color = theme_colors["primary"]
        table.add_row(theme_name.title(), f"[{primary_color}]{primary_color}[/]", description)
    
    console.print(table)

def apply_theme(theme_name: str):
    """Apply a specific theme."""
    if theme_name in THEMES:
        # For now, just return the theme name to indicate selection
        # In a full implementation, we'd update the console theme
        return theme_name
    else:
        return None