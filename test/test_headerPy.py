from pathlib import Path, PosixPath
import re
from typing import List
import pytest
import mock
from mock import MagicMock, call, mock_open

from app.main import HeaderPy, _get_bool


class TestHeaderRCSettings:
    @classmethod
    def setup_class(cls):
        """
        Runs 1 time before all tests in this class
        """
        pass

    def test_get_bool(self):
        input_val = {"test": "TRUE", "something": ""}
        assert _get_bool(input_val, "test") == True
        input_val = {"something": "", "test": "true"}
        assert _get_bool(input_val, "test") == True
        input_val = {"test": "false", "something": ""}
        assert _get_bool(input_val, "test") == False
        input_val = {"NO": "false", "something": ""}
        assert _get_bool(input_val, "test", default=True) == True
        assert _get_bool({}, "test", default=False) == False

    @mock.patch.object(Path, "is_file")
    @mock.patch("os.walk")
    @mock.patch.object(HeaderPy, "_add_header_to_file")
    def test_loop_through_files_opt_out(
        self, _add_header_to_file: MagicMock, mockwalk: MagicMock, mock_is_file: MagicMock
    ):
        mw: List[tuple] = [
            ("/foo", (), ("bad.sh")),
            ("/foo/bar", (), ("spam.md", "eggs.js")),
        ]
        mockwalk.return_value = mw
        mock_is_file.return_value = True

        h = HeaderPy(dry_run=True, verbose=False)
        h.header_rc.header = "Header"
        h.header_rc._file_associations = {".js": "//", ".sh": "#", ".txt": "", "\\.md$": ["<!--", "-->"]}

        ignores = [re.compile(r"bad")]
        h._loop_through_files_opt_out(ignores)

        assert _add_header_to_file.call_count == 2

        assert _add_header_to_file.call_args_list == [
            call(
                PosixPath("../../foo/bar/spam.md"),
                PosixPath("../../foo/bar/spam.md"),
                "<!-- Header -->\n",
                None,
                ("<!--", "-->"),
            ),
            call(
                PosixPath("../../foo/bar/eggs.js"), PosixPath("../../foo/bar/eggs.js"), "// Header \n", None, ("//", "")
            ),
        ]
