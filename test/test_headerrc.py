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
        # TODO: Test ignores
        # TODO: Test accepts
        
    def test_paths(self, _load_default_yml: MagicMock, _load_user_yml: MagicMock):
        h = HeaderRC(unit_test_mode=True, use_default_paths=False)
        assert h.home_path == Path("")
        assert h.work_path == Path("")
        
        h = HeaderRC(unit_test_mode=True, use_default_paths=True)
        assert h.home_path == Path("/app/")
        assert h.work_path == Path("/github/workspace")
        
    def test_load_yml_once(self, _load_default_yml: MagicMock, _load_user_yml: MagicMock):
        HeaderRC(unit_test_mode=True)
        _load_default_yml.assert_called_once()
        _load_user_yml.assert_called_once()

    def test_file_mode(self, _load_default_yml: MagicMock, _load_user_yml: MagicMock):
        mock_yml = {
            "file_mode": "opt-out",
        }
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
        mock_yml = {
            "negagate_characters": "++",
        }
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
