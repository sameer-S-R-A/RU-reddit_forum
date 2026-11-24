#!/usr/bin/env python
"""Run Django commands from Sameer's project folder."""
import os
import sys
from pathlib import Path


def main():
    team_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(team_root))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reddit_forum.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
