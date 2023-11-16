import pytest

from app.main import HeaderPy
from app.headerrc import HeaderRC, File_Mode
import mock
from mock import MagicMock
from pathlib import Path


# All functions in this class have mocks
@mock.patch.object(HeaderRC, "_load_default_yml")
@mock.patch.object(HeaderRC, "_load_user_yml")
class TestHeaderRCSettings:
    @classmethod
    def setup_class(cls):
        """
        Runs 1 time before all tests in this class
        """
        # TODO: Test _file_associations: dict = {}
        # TODO: Test file_associations_by_comment: dict = {}
        # TODO: Test file_associations_by_extension: dict = {}
        # TODO: Test use_default_file_settings
        # TODO: Test untrack_gitignore_enabled
        # TODO: Test _skip_lines_that_have_raw

        # TODO: Test negagate in accepts
        # TODO: Test negagate in ignores
        # TODO: Test negagate in file_associations_by_extension
        # TODO: Test negagate in file_associations_by_comment

    def test_accepts(self, _load_default_yml: MagicMock, _load_user_yml: MagicMock):
        mock_yml = {"tracked_files": []}
        mock_yml_user = {"file_mode": "opt-in", "tracked_files": [r"^README.md$"]}

        _load_default_yml.return_value = mock_yml
        _load_user_yml.return_value = mock_yml_user

        h = HeaderRC(unit_test_mode=True)
        assert set(h.accepts_str) == set([r"^README.md$"])

        mock_yml["tracked_files"] = [
            r"^Dockerfile$",
        ]
        mock_yml_user["tracked_files"] = [
            r"docker-compose.yml",
            r"^README.md$",
        ]
        h = HeaderRC(unit_test_mode=True)

        assert set(h.accepts_str) == set([r"^README.md$", r"docker-compose.yml", r"^Dockerfile$"])

    def test_ignores(self, _load_default_yml: MagicMock, _load_user_yml: MagicMock):
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

    def test_untrack_gitignore_enabled_value(self, _load_default_yml: MagicMock, _load_user_yml: MagicMock):
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

    def test_use_default_file_setting_value(self, _load_default_yml: MagicMock, _load_user_yml: MagicMock):
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

    def test_file_mode(self, _load_default_yml: MagicMock, _load_user_yml: MagicMock):
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

    def test_negagate_characters(self, _load_default_yml: MagicMock, _load_user_yml: MagicMock):
        mock_yml = {"negagate_characters": "++"}
        _load_default_yml.return_value = mock_yml
        _load_user_yml.return_value = mock_yml

        h = HeaderRC(unit_test_mode=True)
        assert h.negate_characters == "++"

        mock_yml["negagate_characters"] = "!"
        _load_user_yml.return_value = mock_yml
        h = HeaderRC(unit_test_mode=True)
        assert h.negate_characters == "!"

        del mock_yml["negagate_characters"]
        _load_user_yml.return_value = mock_yml
        h = HeaderRC(unit_test_mode=True)
        assert h.negate_characters == "!"
