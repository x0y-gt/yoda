import json
import subprocess
import sys


class TestCLIIntegration:
    def test_run_simple_task(self, tmp_path, monkeypatch):
        """Test running a simple echo command"""
        config = {
            "projects": {
                "demo": {
                    "tasks": {
                        "hello": "echo hello"
                    }
                }
            }
        }
        (tmp_path / "yoda.json").write_text(json.dumps(config))
        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "yoda.cli", "demo", "hello"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "hello" in result.stdout

    def test_task_with_params(self, tmp_path, monkeypatch):
        """Test variable substitution via CLI override"""
        config = {
            "projects": {
                "demo": {
                    "tasks": {
                        "greet": {
                            "params": ["NAME"],
                            "run": "echo Hello ${NAME}"
                        }
                    }
                }
            }
        }
        (tmp_path / "yoda.json").write_text(json.dumps(config))
        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "yoda.cli", "demo", "greet", "NAME=World"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "World" in result.stdout

    def test_missing_project_fails(self, tmp_path, monkeypatch):
        """Test error handling for missing project"""
        config = {"projects": {}}
        (tmp_path / "yoda.json").write_text(json.dumps(config))
        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "yoda.cli", "nonexistent", "task"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 1
        assert "not found" in result.stdout

    def test_missing_required_param_fails(self, tmp_path, monkeypatch):
        """Test error when required param is missing"""
        config = {
            "projects": {
                "demo": {
                    "tasks": {
                        "deploy": {
                            "params": ["TAG"],
                            "run": "echo ${TAG}"
                        }
                    }
                }
            }
        }
        (tmp_path / "yoda.json").write_text(json.dumps(config))
        monkeypatch.chdir(tmp_path)

        result = subprocess.run(
            [sys.executable, "-m", "yoda.cli", "demo", "deploy"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 1
        assert "Missing required param" in result.stdout

    def test_shell_features_enabled(self, tmp_path, monkeypatch):
        """Test that shell features are enabled (no escaping)"""
        config = {
            "projects": {
                "demo": {
                    "tasks": {
                        "echo": {
                            "params": ["MSG"],
                            "run": "echo ${MSG}"
                        }
                    }
                }
            }
        }
        (tmp_path / "yoda.json").write_text(json.dumps(config))
        monkeypatch.chdir(tmp_path)

        # Try to use a shell feature
        # We use expr 1 + 1 which should output 2 if executed by shell
        # If escaped, it would print the literal string $(expr 1 + 1)
        result = subprocess.run(
            [
                sys.executable, "-m", "yoda.cli", "demo", "echo", "MSG=$(expr 1 + 1)"
            ],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        # Should execute and print 2
        # We look for "2" in the output. 
        # Note: log message will contain $(expr 1 + 1) so we can't assert it's missing.
        # But "2" should NOT appear if it was just printing the literal string.
        assert "2" in result.stdout
