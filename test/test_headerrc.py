import re
import pytest
import mock
from mock import MagicMock, mock_open

from app.headerrc import HeaderRC, File_Mode


# All functions in this class have mocks
@mock.patch.object(HeaderRC, "_load_default_yml")
@mock.patch.object(HeaderRC, "_load_user_yml")
class TestHeaderRCSettings:
    @classmethod
    def setup_class(cls):
        """
        Runs 1 time before all tests in this class
        """
        pass

    def test_negate_ignores(self, _load_user_yml: MagicMock, _load_default_yml: MagicMock):
        mock_yml = {"untracked_files": [r"^README.md$", r"test.txt"], "untrack_gitignore": False}
        mock_yml_user = {"file_mode": "opt-out", "untracked_files": [r"!^README.md$", r"^Dockerfile$", r"test.txt"]}

        _load_default_yml.return_value = mock_yml
        _load_user_yml.return_value = mock_yml_user

        h = HeaderRC(unit_test_mode=True)
        assert set(h.ignores_str) == set([r"^Dockerfile$", r"test.txt"])

        mock_yml["untracked_files"] = [r"^README.md$", r"test.txt"]
        mock_yml_user["untracked_files"] = [r"!^README.md$", r"README.md"]
        h = HeaderRC(unit_test_mode=True)
        assert set(h.ignores_str) == set([r"README.md", r"test.txt"])

    def test_negate_accepts(self, _load_user_yml: MagicMock, _load_default_yml: MagicMock):
        mock_yml = {"tracked_files": [r"^README.md$", r"test.txt"]}
        mock_yml_user = {"file_mode": "opt-in", "tracked_files": [r"!^README.md$", r"^Dockerfile$", r"test.txt"]}

        _load_default_yml.return_value = mock_yml
        _load_user_yml.return_value = mock_yml_user

        h = HeaderRC(unit_test_mode=True)
        assert set(h.accepts_str) == set([r"^Dockerfile$", r"test.txt"])

        mock_yml["tracked_files"] = [r"^README.md$", r"test.txt"]
        mock_yml_user["tracked_files"] = [r"!^README.md$", r"README.md"]
        h = HeaderRC(unit_test_mode=True)
        assert set(h.accepts_str) == set([r"README.md", r"test.txt"])

    def test_accepts(self, _load_user_yml: MagicMock, _load_default_yml: MagicMock):
        mock_yml = {"tracked_files": []}
        mock_yml_user = {"file_mode": "opt-in", "tracked_files": [r"^README.md$"]}

        _load_default_yml.return_value = mock_yml
        _load_user_yml.return_value = mock_yml_user

        h = HeaderRC(unit_test_mode=True)
        assert set(h.accepts_str) == set([r"^README.md$"])

        mock_yml["tracked_files"] = [r"^Dockerfile$"]
        mock_yml_user["tracked_files"] = [r"docker-compose.yml", r"^README.md$"]
        h = HeaderRC(unit_test_mode=True)

        assert set(h.accepts_str) == set([r"^README.md$", r"docker-compose.yml", r"^Dockerfile$"])

    def test_ignores(self, _load_user_yml: MagicMock, _load_default_yml: MagicMock):
        mock_yml = {"untracked_files": [r"^\.git/", r"^\.gitignore"]}
        mock_yml_user = {"untracked_files": [r"^\.git/", r"^\.gitignore"], "untrack_gitignore": False}

        _load_default_yml.return_value = mock_yml
        _load_user_yml.return_value = mock_yml_user

        h = HeaderRC(unit_test_mode=True)
        assert set(h.ignores_str) == set([r"^\.git/", r"^\.gitignore"])

        mock_yml_user["untracked_files"] = [
            r"^\.git/",
            r"docker-compose.yml",
            r"^Dockerfile$",
        ]
        h = HeaderRC(unit_test_mode=True)

        assert set(h.ignores_str) == set([r"^\.git/", r"^\.gitignore", r"docker-compose.yml", r"^Dockerfile$"])

    def test_untrack_gitignore_enabled_value(self, _load_user_yml: MagicMock, _load_default_yml: MagicMock):
        mock_yml = {"untrack_gitignore": True}

        _load_default_yml.return_value = mock_yml
        _load_user_yml.return_value = mock_yml

        h = HeaderRC(unit_test_mode=True)
        assert h.untrack_gitignore == True

        mock_yml["untrack_gitignore"] = False
        _load_user_yml.return_value = mock_yml
        h = HeaderRC(unit_test_mode=True)
        assert h.untrack_gitignore == False

        del mock_yml["untrack_gitignore"]
        _load_user_yml.return_value = mock_yml
        h = HeaderRC(unit_test_mode=True)
        assert h.untrack_gitignore == True

    def test_use_default_file_setting_value(self, _load_user_yml: MagicMock, _load_default_yml: MagicMock):
        mock_yml = {"use_default_file_settings": True}

        _load_default_yml.return_value = mock_yml
        _load_user_yml.return_value = mock_yml

        h = HeaderRC(unit_test_mode=True)
        assert h.use_default_file_settings == True

        mock_yml["use_default_file_settings"] = False
        _load_user_yml.return_value = mock_yml
        h = HeaderRC(unit_test_mode=True)
        assert h.use_default_file_settings == False

        del mock_yml["use_default_file_settings"]
        _load_user_yml.return_value = mock_yml
        h = HeaderRC(unit_test_mode=True)
        assert h.use_default_file_settings == True

    def test_file_mode(self, _load_user_yml: MagicMock, _load_default_yml: MagicMock):
        mock_yml = {"file_mode": "opt-out"}
        _load_default_yml.return_value = mock_yml
        _load_user_yml.return_value = mock_yml

        h = HeaderRC(unit_test_mode=True)
        assert h.file_mode == File_Mode.OPT_OUT

        mock_yml["file_mode"] = "opt-in"
        _load_user_yml.return_value = mock_yml
        h = HeaderRC(unit_test_mode=True)
        assert h.file_mode == File_Mode.OPT_IN

        del mock_yml["file_mode"]
        _load_user_yml.return_value = mock_yml
        h = HeaderRC(unit_test_mode=True)
        assert h.file_mode == File_Mode.OPT_OUT

    def test_negate_characters(self, _load_user_yml: MagicMock, _load_default_yml: MagicMock):
        mock_yml = {"negate_characters": "++"}
        _load_default_yml.return_value = mock_yml
        _load_user_yml.return_value = mock_yml

        h = HeaderRC(unit_test_mode=True)
        assert h.negate_characters == "++"

        mock_yml["negate_characters"] = "!"
        _load_user_yml.return_value = mock_yml
        h = HeaderRC(unit_test_mode=True)
        assert h.negate_characters == "!"

        del mock_yml["negate_characters"]
        _load_user_yml.return_value = mock_yml
        h = HeaderRC(unit_test_mode=True)
        assert h.negate_characters == "!"

    def test_file_associations(self, _load_user_yml: MagicMock, _load_default_yml: MagicMock):
        mock_yml = {
            "file_associations_by_comment": {
                "#": ["^.gitignore$"],
                "//": [".js$", ".ts$"],
            },
            "file_associations_by_extension": {
                ".md": ["<!--", "-->"],
            },
        }
        mock_yml_user = {}

        _load_default_yml.return_value = mock_yml
        _load_user_yml.return_value = mock_yml_user

        h = HeaderRC(unit_test_mode=True)
        assert h.file_associations == {
            "^.gitignore$": "#",
            ".js$": "//",
            ".ts$": "//",
            ".md": ["<!--", "-->"],
        }

        mock_yml_user = {
            "file_associations_by_comment": {
                "#": ["\\.*\\.ya?ml$"],
            },
            "file_associations_by_extension": {"\\.html$": ["<!--", "-->"]},
        }

        _load_default_yml.return_value = mock_yml
        _load_user_yml.return_value = mock_yml_user

        h = HeaderRC(unit_test_mode=True)
        assert h.file_associations == {
            "\\.*\\.ya?ml$": "#",
            "^.gitignore$": "#",
            ".js$": "//",
            ".ts$": "//",
            ".md": ["<!--", "-->"],
            "\\.html$": ["<!--", "-->"],
        }

    def test_negate_file_associations_by_comment(self, _load_user_yml: MagicMock, _load_default_yml: MagicMock):
        mock_default_yml = {
            "file_associations_by_comment": {
                "//": [".js$", ".ts$"],
            },
        }
        mock_user_yml = {
            "file_associations_by_comment": {
                "//": ["!.js$"],
            },
        }

        _load_default_yml.return_value = mock_default_yml
        _load_user_yml.return_value = mock_user_yml

        h = HeaderRC(unit_test_mode=True)

        assert h.file_associations == {
            ".ts$": "//",
        }

    def test_negate_file_associations_by_extension(self, _load_user_yml: MagicMock, _load_default_yml: MagicMock):
        mock_default_yml = {
            "file_associations_by_extension": {".md": ["<!--", "-->"], "\\.html$": ["<!--", "-->"]},
        }
        mock_user_yml = {
            "file_associations_by_extension": {
                "!.md": ["<!--", "-->"],
                ".md": ["<#--", "--#>"],
            },
        }

        _load_default_yml.return_value = mock_default_yml
        _load_user_yml.return_value = mock_user_yml

        h = HeaderRC(unit_test_mode=True)
        assert h.file_associations == {
            "\\.html$": ["<!--", "-->"],
            ".md": ["<#--", "--#>"],
        }

    def test_skip_lines_that_have_raw(self, _load_user_yml: MagicMock, _load_default_yml: MagicMock):
        mock_default_yml = {
            "skip_lines_that_have": {".sh$": ["#!"]},
        }
        mock_user_yml = {
            "skip_lines_that_have": {".test": ["!test"], ".sh$": ["#!/bin/sh"]},
        }

        _load_default_yml.return_value = mock_default_yml
        _load_user_yml.return_value = mock_user_yml

        h = HeaderRC(unit_test_mode=True)

        assert h._skip_lines_that_have_raw == {
            ".test": ["!test"],
            ".sh$": ["#!", "#!/bin/sh"],
        }

    @mock.patch("builtins.open", mock_open(read_data="# Environments\n \nbaz\n foo\n"))
    def test_untrack_gitignore(self, _load_user_yml: MagicMock, _load_default_yml: MagicMock):
        h = HeaderRC(
            unit_test_mode=True,
        )

        mock_yml = {"untracked_files": [r"^README.md$", r"test.txt"], "untrack_gitignore": False}
        mock_yml_user = {"file_mode": "opt-out", "untracked_files": [r"!^README.md$", r"^Dockerfile$", r"test.txt"]}
        mock_yml["file_mode"] = "opt-out"

        _load_default_yml.return_value = mock_yml
        _load_user_yml.return_value = mock_yml_user

        h = HeaderRC(unit_test_mode=True)
        assert set(h.ignores_str) == set([r"^Dockerfile$", r"test.txt"])

        mock_yml_user["untrack_gitignore"] = True

        _load_user_yml.return_value = mock_yml_user

        h = HeaderRC(unit_test_mode=True)
        assert set(h.ignores_str) == set([r"^Dockerfile$", r"test.txt", "baz", "foo"])

    def test_use_default_file_settings(self, _load_user_yml: MagicMock, _load_default_yml: MagicMock):
        mock_yml = {
            "untracked_files": [r"^README.md$", r"test.txt"],
            "tracked_files": [r"^\.git/", r"^\.gitignore"],
            "file_associations_by_comment": {"//": [".js$", ".ts$"]},
            "file_associations_by_extension": {".md": ["<!--", "-->"]},
            "skip_lines_that_have": {".sh$": ["#&"]},
        }
        mock_yml_user = {"use_default_file_settings": True, "untrack_gitignore": False, "file_mode": "opt-out"}

        _load_default_yml.return_value = mock_yml
        _load_user_yml.return_value = mock_yml_user

        h = HeaderRC(unit_test_mode=True)
        assert set(h.ignores_str) == set([r"^README.md$", r"test.txt"])
        assert h.file_associations == {
            ".js$": "//",
            ".ts$": "//",
            ".md": ["<!--", "-->"],
        }
        assert h._skip_lines_that_have_raw == {".sh$": ["#&"]}

        mock_yml_user["file_mode"] = "opt-in"

        h = HeaderRC(unit_test_mode=True)
        assert set(h.accepts_str) == set([r"^\.git/", r"^\.gitignore"])

        mock_yml_user["use_default_file_settings"] = False
        h = HeaderRC(unit_test_mode=True)
        assert set(h.accepts_str) == set()
        assert h.file_associations == {}
        assert h._skip_lines_that_have_raw == {}

        mock_yml_user["file_mode"] = "opt-out"
        h = HeaderRC(unit_test_mode=True)
        assert set(h.ignores_str) == set()

    @mock.patch("builtins.print", return_value=None)
    def test_verbose(self, _mockcprint: MagicMock, _load_user_yml: MagicMock, _load_default_yml: MagicMock):
        h = HeaderRC(unit_test_mode=True, verbose=True)
        assert True

    def test_dict_to_regex(self, _load_user_yml: MagicMock, _load_default_yml: MagicMock):
        mock_yml = {
            "file_associations_by_comment": {
                "#": ["^.gitignore$"],
            },
            "file_associations_by_extension": {
                ".md": ["<!--", "-->"],
            },
        }
        mock_yml_user = {"untrack_gitignore": False}

        _load_default_yml.return_value = mock_yml
        _load_user_yml.return_value = mock_yml_user

        h = HeaderRC(unit_test_mode=True)
        val = {
            re.compile("^.gitignore$"): "#",
            re.compile(".md"): ["<!--", "-->"],
        }
        assert h.file_associations_regex == val

    def test_get_header(self, _load_user_yml: MagicMock, _load_default_yml: MagicMock):
        mock_yml = {"header": "Starter header"}
        mock_yml_user = {"header": "NOT header"}

        _load_default_yml.return_value = mock_yml
        _load_user_yml.return_value = mock_yml_user

        h = HeaderRC(unit_test_mode=True)
        assert h.header == "NOT header"

    def test_get_header_for_file(self, _load_user_yml: MagicMock, _load_default_yml: MagicMock):
        mock_yml = {
            "header": "Starter header",
            "file_associations_by_comment": {
                "//": [".js$", ".ts$"],
            },
        }
        mock_yml_user = {"header": "NOT header"}

        _load_default_yml.return_value = mock_yml
        _load_user_yml.return_value = mock_yml_user

        h = HeaderRC(unit_test_mode=True)
        assert h.get_header_for_file("test.ts") == ("// NOT header \n", "//", "", True)

    def test_get_skip_lines_that_start_for_file(self, _load_user_yml: MagicMock, _load_default_yml: MagicMock):
        mock_yml = {
            "file_associations_by_comment": {
                "#": [".sh$"],
            },
            "skip_lines_that_have": {"\\.sh$": ["^#!"]},
        }
        mock_yml_user = {}

        _load_default_yml.return_value = mock_yml
        _load_user_yml.return_value = mock_yml_user

        h = HeaderRC(unit_test_mode=True)
        assert h.get_skip_lines_that_start_for_file("test.sh") == [re.compile("^#!")]


class TestHeaderRCLoadYML:
    @classmethod
    def setup_class(cls):
        """
        Runs 1 time before all tests in this class
        """
        pass

    def test_load_yml(self):
        h = HeaderRC(unit_test_mode=True, use_default_paths=True)
