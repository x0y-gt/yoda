#!/usr/bin/env python3
import os
import sys
import json
import shlex
import subprocess
from dotenv import load_dotenv, find_dotenv

# Locate and load the .env in the repo root (override anything already set).
# The .env file is optional - if not found, only existing env vars will be used.
dotenv_path = os.path.join(os.getcwd(), ".env")
dotenv = find_dotenv(
    filename=dotenv_path, raise_error_if_not_found=False
)
if dotenv:
    load_dotenv(dotenv, override=True)


def load_config(path="yoda.json"):
    try:
        with open(path) as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"❌ Config file '{path}' not found")
        print("   Create a yoda.json file in the current directory")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in '{path}': {e.msg} (line {e.lineno})")
        sys.exit(1)

    if "projects" not in config:
        print(f"❌ Config file '{path}' missing required 'projects' key")
        sys.exit(1)

    return config


def resolve_vars(
    template: str, context: dict, shell_escape: bool = False
) -> str:
    """Replace ${VAR} placeholders with values from context.

    Args:
        template: String containing ${VAR} placeholders
        context: Dict of variable names to values
        shell_escape: If True, escape values to prevent shell injection
    """
    for key, val in context.items():
        safe_val = shlex.quote(val) if shell_escape else val
        template = template.replace(f"${{{key}}}", safe_val)
    return template


def run_task(project: str, task_name: str, config: dict, overrides: dict):
    proj = config["projects"].get(project)
    if not proj:
        print(f"❌ Project '{project}' not found")
        sys.exit(1)

    raw_env = proj.get("env", {})

    # Build a master context:
    #    - everything from os.environ (after load_dotenv)
    #    - then any CLI overrides (TAG=…, etc.)
    context = dict(os.environ)
    context.update(overrides)

    # Resolve JSON `env` keys against that context
    project_env = {}
    for k, tmpl in raw_env.items():
        project_env[k] = resolve_vars(tmpl, context)

    # Quick sanity‐check:
    #    ensure none of your project_env values still look like "${…}"
    bad = {k: v for k, v in project_env.items() if "${" in v}
    if bad:
        print("❌ These env vars weren’t resolved (check your .env keys!):")
        for k, v in bad.items():
            print(f"   • {k} = {v}")
        sys.exit(1)

    # Merge into final_env for command interpolation
    final_env = dict(context)
    final_env.update(project_env)

    # Lookup & validate the task
    tasks = proj.get("tasks")
    if not tasks:
        print(f"❌ Project '{project}' has no 'tasks' defined")
        sys.exit(1)

    task = tasks.get(task_name)
    if not task:
        print(f"❌ Task '{task_name}' not found in project '{project}'")
        sys.exit(1)

    # Enforce required params (if any)
    #    Params ending with "?" are optional (e.g., "MESSAGE?")
    params = task.get("params", []) if isinstance(task, dict) else []
    required_params = [p for p in params if not p.endswith("?")]
    optional_params = [p.rstrip("?") for p in params if p.endswith("?")]

    missing = [p for p in required_params if p not in final_env]
    if missing:
        print(
            f"❌ Missing required param(s) {missing} for '{project}:{task_name}'"
        )
        sys.exit(1)

    # Set empty string for missing optional params
    for p in optional_params:
        if p not in final_env:
            final_env[p] = ""

    # Run any "pre" tasks
    if isinstance(task, dict):
        for pre in task.get("pre", []):
            run_task(project, pre, config, overrides)
        cmd_tmpl = task.get("run")
        if not cmd_tmpl:
            print(f"❌ Task '{task_name}' missing required 'run' command")
            sys.exit(1)
    else:
        cmd_tmpl = task

    # Final macro‐substitution (with shell escaping to prevent injection)
    cmd = resolve_vars(cmd_tmpl, final_env, shell_escape=True)
    print(f"→ Executing: {cmd}\n")

    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Command failed with exit code {e.returncode}")
        sys.exit(e.returncode)


def main():
    if len(sys.argv) < 3:
        print("Usage: must <project> <task> [KEY=VALUE...]")
        sys.exit(1)

    project, task_name, *rest = sys.argv[1:]
    overrides = {}
    for arg in rest:
        if "=" in arg:
            key, val = arg.split("=", 1)
            overrides[key] = val
        else:
            print(f"❌ Invalid argument '{arg}' - expected KEY=VALUE format")
            sys.exit(1)

    try:
        cfg = load_config()
        run_task(project, task_name, cfg, overrides)
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted")
        sys.exit(130)


if __name__ == "__main__":
    main()
