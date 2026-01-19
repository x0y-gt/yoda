import json
import pytest
from yoda.cli import resolve_vars, load_config


class TestResolveVars:
    def test_basic_substitution(self):
        template = "Hello ${NAME}!"
        context = {"NAME": "World"}
        result = resolve_vars(template, context)
        assert result == "Hello World!"

    def test_multiple_vars(self):
        template = "${GREETING} ${NAME}, welcome to ${PLACE}"
        context = {"GREETING": "Hello", "NAME": "Alice", "PLACE": "Wonderland"}
        result = resolve_vars(template, context)
        assert result == "Hello Alice, welcome to Wonderland"

    def test_missing_var_unchanged(self):
        template = "Hello ${NAME}!"
        context = {"OTHER": "value"}
        result = resolve_vars(template, context)
        assert result == "Hello ${NAME}!"

    def test_shell_escape_simple(self):
        template = "echo ${MSG}"
        context = {"MSG": "hello"}
        result = resolve_vars(template, context, shell_escape=True)
        assert result == "echo hello"

    def test_shell_escape_with_spaces(self):
        template = "echo ${MSG}"
        context = {"MSG": "hello world"}
        result = resolve_vars(template, context, shell_escape=True)
        assert result == "echo 'hello world'"

    def test_shell_escape_prevents_injection(self):
        template = "echo ${MSG}"
        context = {"MSG": "$(rm -rf /)"}
        result = resolve_vars(template, context, shell_escape=True)
        assert "'" in result or '"' in result
        assert result != "echo $(rm -rf /)"

    def test_shell_escape_special_chars(self):
        template = "echo ${MSG}"
        context = {"MSG": "; cat /etc/passwd"}
        result = resolve_vars(template, context, shell_escape=True)
        assert result == "echo '; cat /etc/passwd'"


class TestLoadConfig:
    def test_file_not_found(self, tmp_path):
        with pytest.raises(SystemExit) as exc_info:
            load_config(str(tmp_path / "nonexistent.json"))
        assert exc_info.value.code == 1

    def test_invalid_json(self, tmp_path):
        config_file = tmp_path / "invalid.json"
        config_file.write_text("{ invalid json }")
        with pytest.raises(SystemExit) as exc_info:
            load_config(str(config_file))
        assert exc_info.value.code == 1

    def test_missing_projects_key(self, tmp_path):
        config_file = tmp_path / "yoda.json"
        config_file.write_text(json.dumps({"other": "data"}))
        with pytest.raises(SystemExit) as exc_info:
            load_config(str(config_file))
        assert exc_info.value.code == 1

    def test_valid_config(self, tmp_path):
        config_file = tmp_path / "yoda.json"
        expected = {"projects": {"myapp": {"tasks": {}}}}
        config_file.write_text(json.dumps(expected))
        result = load_config(str(config_file))
        assert result == expected
