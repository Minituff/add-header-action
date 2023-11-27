from pathlib import Path, PosixPath
import re
from typing import List
import pytest
import mock
from mock import MagicMock, call, mock_open

from app.main import HeaderPy, _get_bool, main
from app.headerrc import File_Mode, Header_Action


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
        assert _get_bool({"test": "fake"}, "test", default=True) == True

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

        h = HeaderPy(dry_run=True, verbose=True, unit_test_mode=True)
        h.header_rc.header = "Header"
        h.header_action = Header_Action.ADD
        h.header_rc._file_associations = {".js": "//", ".sh": "#", ".txt": "", "\\.md$": ["<!--", "-->"]}

        ignores = [re.compile(r"bad")]
        h._loop_through_files_opt_out(ignores)

        assert _add_header_to_file.call_count == 2

        for idx, call in enumerate(_add_header_to_file.call_args_list):
            (path1, path2, header, skip_prefixes, prefix_suffix) = call.args

            if idx == 0:
                assert str(path1).endswith("foo/bar/spam.md")
                assert str(path2).endswith("foo/bar/spam.md")
                assert skip_prefixes == None
                assert header == "<!-- Header -->\n"
                assert prefix_suffix == ("<!--", "-->")
            if idx == 1:
                assert str(path1).endswith("foo/bar/eggs.js")
                assert str(path1).endswith("foo/bar/eggs.js")
                assert skip_prefixes == None
                assert header == "// Header \n"
                assert prefix_suffix == ("//", "")

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

        h = HeaderPy(dry_run=True, verbose=True, unit_test_mode=True)
        h.header_rc.header = "Header"
        h.header_rc.file_mode = File_Mode.OPT_OUT
        h.header_action = Header_Action.ADD
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

        h = HeaderPy(dry_run=False, verbose=True, unit_test_mode=True)
        h._add_header_to_file(
            file_path=tmp_path, relative_file_path=tmp_path, header="# HEADER", prefix_suffix=("#", "")
        )

        with tmp_path.open("r+", encoding="utf-8") as file:
            contents = file.read()
            assert contents == "# HEADER\n\nSome basic stuff"

    @mock.patch("builtins.print", return_value=None)
    def test_add_header_to_file_where_already_exists(self, mock_print: MagicMock, tmp_path: Path):
        tmp_path = tmp_path / "tmp-file.txt"
        with tmp_path.open("a", encoding="utf-8") as f:
            f.write("# HEADER\n\nSome basic stuff")

        h = HeaderPy(dry_run=False, verbose=True, unit_test_mode=True)
        h._add_header_to_file(
            file_path=tmp_path, relative_file_path=tmp_path, header="# HEADER", prefix_suffix=("#", "")
        )

        with tmp_path.open("r+", encoding="utf-8") as file:
            contents = file.read()
            assert contents == "# HEADER\n\nSome basic stuff"

    @mock.patch("builtins.print", return_value=None)
    def test_skip_prefixes(self, mock_print: MagicMock, tmp_path: Path):
        tmp_path = tmp_path / "tmp-file.sh"
        with tmp_path.open("a", encoding="utf-8") as f:
            f.write("#!/usr/bin/env bash\n")
            f.write("Some basic stuff\n")

        h = HeaderPy(dry_run=False, verbose=True, unit_test_mode=True)
        h._add_header_to_file(
            file_path=tmp_path,
            relative_file_path=tmp_path,
            header="# HEADER",
            prefix_suffix=("#", ""),
            skip_prefixes=[re.compile("^#!")],
        )

        with tmp_path.open("r+", encoding="utf-8") as file:
            contents = file.read()
            assert contents == "#!/usr/bin/env bash\n\n# HEADER\n\nSome basic stuff\n"

    @mock.patch.object(HeaderPy, "_loop_through_files_opt_out")
    @mock.patch.object(HeaderPy, "_loop_through_files_opt_in")
    @mock.patch("builtins.print", return_value=None)
    def test_run(
        self,
        mock_print: MagicMock,
        mock_loop_through_files_opt_in: MagicMock,
        mock_loop_through_files_opt_out: MagicMock,
    ):
        h = HeaderPy(dry_run=True, verbose=True, unit_test_mode=True)
        h.file_mode = File_Mode.OPT_OUT
        h.run()

        mock_loop_through_files_opt_out.assert_called_once()

        h.file_mode = File_Mode.OPT_IN
        h.run()
        mock_loop_through_files_opt_in.assert_called_once()

    @mock.patch.object(HeaderPy, "__init__", return_value=None)
    @mock.patch.object(HeaderPy, "run", return_value=None)
    @mock.patch("builtins.print", return_value=None)
    def test_arg_parse_default(self, mock_print: MagicMock, mockHeaderPyRun: MagicMock, mockHeaderPy: MagicMock):
        test_input = ["--unit-test-mode", "true"]
        main(test_input)

        args, kwargs = mockHeaderPy.call_args_list[0]
        assert kwargs["verbose"] == False
        assert kwargs["dry_run"] == False
        assert kwargs["unit_test_mode"] == True

    @mock.patch.object(HeaderPy, "__init__", return_value=None)
    @mock.patch.object(HeaderPy, "run", return_value=None)
    @mock.patch("builtins.print", return_value=None)
    def test_arg_parse(self, mock_print: MagicMock, mockHeaderPyRun: MagicMock, mockHeaderPy: MagicMock):
        test_input = ["--unit-test-mode", "true", "--dry-run", "true", "--verbose", "true"]
        main(test_input)

        args, kwargs = mockHeaderPy.call_args_list[0]
        assert kwargs["dry_run"] == True
        assert kwargs["verbose"] == True
