#!/usr/bin/env python
import os
import sys
import pathlib

if __name__ == "__main__":
    # Add test_project/* to PATH so `import testapp` works correctly
    path = (pathlib.Path(__file__) / "..").resolve()
    sys.path.insert(0, str(path / "test_project"))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_project.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        )
    execute_from_command_line(sys.argv)
