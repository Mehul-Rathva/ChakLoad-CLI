"""Template management system for test scripts."""
import os
import shutil
from typing import Dict, List
from pathlib import Path
from string import Template
import yaml

from loadtester.utils.logger import logger


class TemplateManager:
    """Manages test script templates for different frameworks."""
    
    def __init__(self, templates_dir: str = None):
        if templates_dir:
            self.templates_dir = Path(templates_dir)
        else:
            # Default to the templates directory in the package
            current_dir = Path(__file__).parent
            self.templates_dir = current_dir.parent / "templates"
        
        # Ensure the templates directory exists
        self.templates_dir.mkdir(parents=True, exist_ok=True)
    
    def list_templates(self, framework: str = None) -> List[str]:
        """List available templates, optionally filtered by framework."""
        templates = []
        
        if framework:
            framework_dir = self.templates_dir / framework
            if framework_dir.exists():
                for file_path in framework_dir.glob("*.py"):
                    templates.append(file_path.name)
                for file_path in framework_dir.glob("*.js"):
                    templates.append(file_path.name)
                for file_path in framework_dir.glob("*.yml"):
                    templates.append(file_path.name)
                for file_path in framework_dir.glob("*.jmx"):
                    templates.append(file_path.name)
        else:
            for framework_dir in self.templates_dir.iterdir():
                if framework_dir.is_dir():
                    for file_path in framework_dir.glob("*"):
                        templates.append(f"{framework_dir.name}/{file_path.name}")
        
        return templates
    
    def get_template_path(self, framework: str, template_name: str) -> Path:
        """Get the path to a specific template."""
        return self.templates_dir / framework / template_name
    
    def load_template(self, framework: str, template_name: str) -> str:
        """Load the content of a template file."""
        template_path = self.get_template_path(framework, template_name)
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template {template_name} not found for framework {framework}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content
    
    def render_template(self, framework: str, template_name: str, context: Dict[str, str]) -> str:
        """Render a template with the provided context."""
        template_content = self.load_template(framework, template_name)
        
        # Use Python's Template for simple variable substitution
        template = Template(template_content)
        
        try:
            rendered_content = template.substitute(**context)
        except KeyError as e:
            logger.error(f"Missing template variable: {e}")
            raise
        
        return rendered_content
    
    def save_rendered_template(self, content: str, output_path: str) -> str:
        """Save rendered template to a file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(output_path)
    
    def create_custom_template(self, framework: str, template_name: str, content: str) -> str:
        """Create a custom template file."""
        template_dir = self.templates_dir / framework
        template_dir.mkdir(exist_ok=True)
        
        template_path = template_dir / template_name
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(template_path)


# Global template manager instance
template_manager = TemplateManager()


def get_template_manager() -> TemplateManager:
    """Get the global template manager instance."""
    return template_manager