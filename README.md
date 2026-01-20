# Yoda

A flexible, config-driven CLI tool designed to orchestrate build, publish, and deploy workflows for your services to a VPS. It functions as a lightweight task runner with environment variable management.

## Features

- **Config-Driven:** Define all your projects and tasks in a simple `yoda.json` file.
- **Environment Management:** Seamless integration with `.env` files and environment variable substitution.
- **Task Dependencies:** Support for `pre` hooks to run prerequisite tasks.
- **Parameter Validation:** Define required and optional parameters for your tasks.

## Installation

### For Users

Install directly via pip:

```bash
pip install .
```

## Configuration

`yoda` requires a `yoda.json` file in your working directory. Here is a minimal example:

```json
{
  "projects": {
    "myweb": {
      "env": { "IMAGE": "ghcr.io/x0y-gt/myweb:${TAG}" },
      "tasks": {
        "deploy": {
          "params": ["TAG"],
          "run": "docker pull ${IMAGE} && docker restart myweb"
        }
      }
    }
  }
}
```

## Usage

The basic syntax is:

```bash
yoda <project> <task> [KEY=VALUE...]
```

### Examples

**Deploy a specific version:**

```bash
yoda myweb deploy TAG=v1.0.1
```

## Development

1. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -e .[dev]
   ```

3. Run tests:
   ```bash
   pytest
   ```

## License

This project is licensed under the terms of the MIT license.
