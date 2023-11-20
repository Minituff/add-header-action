from pathlib import Path, PosixPath
import re
from typing import List
import pytest
import mock
from mock import MagicMock, call, mock_open

from app.main import HeaderPy, _get_bool
from app.headerrc import File_Mode


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
    @mock.patch("builtins.print", return_value=None)
    def test_loop_through_files_opt_out(
        self,
        mock_print: MagicMock,
        _add_header_to_file: MagicMock,
        mockwalk: MagicMock,
        mock_is_file: MagicMock,
    ):
        mw: List[tuple] = [
            ("/foo", (), ("bad.sh")),
            ("/foo/bar", (), ("spam.md", "eggs.js")),
        ]
        mockwalk.return_value = mw
        mock_is_file.return_value = True

        h = HeaderPy(dry_run=True, verbose=True)
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

    @mock.patch.object(Path, "is_file")
    @mock.patch.object(Path, "relative_to")
    @mock.patch("os.walk")
    @mock.patch.object(HeaderPy, "_add_header_to_file")
    @mock.patch("builtins.print", return_value=None)
    def test_loop_through_files_opt_in(
        self,
        mock_print: MagicMock,
        _add_header_to_file: MagicMock,
        mockwalk: MagicMock,
        mock_relative_to: MagicMock,
        mock_is_file: MagicMock,
    ):
        mw: List[tuple] = [
            ("/good", (), ("bad.sh",)),
            ("/foo/bar", (), ("spam.md", "eggs.js")),
        ]
        mockwalk.return_value = mw
        mock_is_file.return_value = True
        mock_relative_to.return_value = "good/path"

        h = HeaderPy(dry_run=True, verbose=True)
        h.header_rc.header = "Header"
        h.header_rc.file_mode = File_Mode.OPT_OUT
        h.header_rc._file_associations = {".js": "//", ".sh": "#", ".txt": "", "\\.md$": ["<!--", "-->"]}

        accepts = [re.compile(r"good")]
        h._loop_through_files_opt_in(accepts)

        assert _add_header_to_file.call_count == 3
        assert _add_header_to_file.call_args_list == [
            call(PosixPath("/good/bad.sh"), "good/path", "# Header \n", [re.compile("^#!")], ("#", "")),
            call(PosixPath("/foo/bar/spam.md"), "good/path", "<!-- Header -->\n", None, ("<!--", "-->")),
            call(PosixPath("/foo/bar/eggs.js"), "good/path", "// Header \n", None, ("//", "")),
        ]

    @mock.patch("builtins.print", return_value=None)
    def test_add_header_to_file(self, mock_print: MagicMock, tmp_path: Path):
        tmp_path = tmp_path / "tmp-file.txt"
        with tmp_path.open("a", encoding="utf-8") as f:
            f.write("Some basic stuff")

        h = HeaderPy(dry_run=False, verbose=True)
        h._add_header_to_file(
            file_path=tmp_path, relative_file_path=tmp_path, header="# HEADER", prefix_suffix=("#", "")
        )

        with tmp_path.open("r+", encoding="utf-8") as file:
            contents = file.read()
            assert contents == "# HEADER\n\nSome basic stuff"
