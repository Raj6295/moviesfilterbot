"""
Handlers package initialization.
This file ensures all handlers are properly loaded when the package is imported.
"""
import os
import importlib
from pathlib import Path

# Import all command handlers
from .commands import *

# Import other handlers
from .callbacks import *
from .client import *

def load_handlers():
    """Dynamically load all handler modules."""
    # Get the directory of this package
    package_dir = Path(__file__).parent
    
    # Load all Python files in the commands directory
    commands_dir = package_dir / 'commands'
    for file in commands_dir.glob('*.py'):
        if file.name != '__init__.py':
            module_name = f"{__package__}.commands.{file.stem}"
            importlib.import_module(module_name)
    
    # Load other handler files
    for file in package_dir.glob('*.py'):
        if file.name not in ('__init__.py', 'client.py'):
            module_name = f"{__package__}.{file.stem}"
            importlib.import_module(module_name)

# Initialize handlers when the package is imported
load_handlers()
