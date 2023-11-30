import os
import sys
from pathlib import Path
from re import Pattern
from typing import Any, List, Optional, Union
import sys
import argparse
from termcolor import cprint

from headerrc import HeaderRC, File_Mode, Header_Action


class HeaderPy:
    def __init__(self, dry_run=False, verbose=False, unit_test_mode=False, file_name=".headerrc.yml") -> None:
        self.dry_run: bool = dry_run
        self.verbose: bool = verbose
        self.file_name: str = file_name
        self.header_rc: HeaderRC = HeaderRC(verbose=verbose, unit_test_mode=unit_test_mode, file_name=file_name)
        self.file_mode: File_Mode = self.header_rc.file_mode
        self.header_action: Header_Action = self.header_rc.header_action

    def run(self) -> None:
        if str(self.file_mode) == str(File_Mode.OPT_OUT):
            self._loop_through_files_opt_out(self.header_rc.ignores)
        elif str(self.file_mode) == str(File_Mode.OPT_IN):
            self._loop_through_files_opt_in(self.header_rc.accepts)

    def _add_header_to_file(
        self,
        file_path: Union[Path, str],
        relative_file_path: Union[Path, str],
        header: str,
        skip_prefixes: Optional[List[Pattern]] = None,
        prefix_suffix: tuple[str, str] = ("", ""),
    ) -> None:
        if isinstance(file_path, str):
            file_path = Path(file_path)

        # Read the beginning of the file to check for the header
        header_bytes = sys.getsizeof(header) + 100

        with file_path.open("r+", encoding="utf-8") as file:
            try:
                start_of_file = file.read(header_bytes)
            except UnicodeDecodeError as e:
                if self.verbose is True:
                    cprint(f"Can't decode - {file_path}", "red")
                return

            if header in start_of_file:
                if self.verbose or self.dry_run:
                    print(f"Header already in - {relative_file_path}")
                return  # Header already present, no need to add it

            if self.dry_run:
                print(f"Would add header to - {relative_file_path} - {prefix_suffix}")
                return
            print(f"Adding header to - {relative_file_path} - {prefix_suffix}")

            file.seek(0, 0)  # Rewind to start of the file for re-reading
            contents = file.read()  # Read the entire file
            lines = contents.split("\n")

            skip_index = 0
            if skip_prefixes:
                if self.verbose:
                    cprint(f"skip_lines_that_start_with enabled for {file_path}", "yellow")

                for i, line in enumerate(lines):
                    for pattern in skip_prefixes:
                        if pattern.search(line):
                            skip_index = i + 1
                            break
                    else:
                        break
                header_formatted = "\n\n" + header.rstrip("\r\n") + "\n\n"
            else:
                header_formatted = header.rstrip("\r\n") + "\n\n"

            modified_content = "\n".join(lines[:skip_index]) + header_formatted + "\n".join(lines[skip_index:])
            file.seek(0, 0)  # Move to the start of the file
            file.write(modified_content)  # Write the modified content
            file.truncate()  # Truncate in case the new content is shorter

    def _remove_header_from_file(
        self,
        file_path: Union[Path, str],
        relative_file_path: Union[Path, str],
        header: str,
    ) -> None:
        if isinstance(file_path, str):
            file_path = Path(file_path)

        header += "\n"
        # Read the beginning of the file to check for the header
        header_bytes = sys.getsizeof(header) + 100

        with file_path.open("r+", encoding="utf-8") as file:
            try:
                start_of_file = file.read(header_bytes)
            except UnicodeDecodeError as e:
                if self.verbose is True:
                    cprint(f"Can't decode - {file_path}", "red")
                return

            if header not in start_of_file:
                if self.verbose or self.dry_run:
                    print(f"Header not in - {relative_file_path}")
                return  # Header not present, no need to remove it

            if self.dry_run:
                print(f"Would remove header from - {relative_file_path}")
                return
            print(f"Removing header from - {relative_file_path}")

            file.seek(0)
            content = file.read()

            # Remove the header from content
            content = content.replace(header, "", 1)

            # Write back the modified content
            file.seek(0)
            file.write(content)
            file.truncate()  # Truncate to remove any leftover content

    def _loop_through_files_opt_in(self, re_accept_patterns: List[Pattern]) -> None:
        base_dir = self.header_rc.work_path

        for root, _, files in os.walk(base_dir, topdown=True):
            for file in files:
                # Create the full path and relative path for each file
                full_file_path = Path(root) / file
                rel_file_path = full_file_path.relative_to(base_dir)

                # Check if the relative path of the file matches any of the accept patterns
                # Skip the file if it does not match
                if not any(pattern.search(str(rel_file_path)) for pattern in re_accept_patterns):
                    if self.verbose and not str(rel_file_path).startswith(".git"):
                        cprint(f"Skip - {rel_file_path}", "yellow")
                    continue

                if not full_file_path.is_file():
                    if self.verbose:
                        cprint(f"Skip (not a file) - {rel_file_path}", "yellow")
                    continue

                header, prefix, suffix, succes = self.header_rc.get_header_for_file(file)
                if succes:
                    if str(self.header_action) == str(Header_Action.REMOVE):
                        self._remove_header_from_file(full_file_path, rel_file_path, header)
                    elif str(self.header_action) == str(Header_Action.ADD):
                        skip_prefixes = self.header_rc.get_skip_lines_that_start_for_file(file)
                        self._add_header_to_file(full_file_path, rel_file_path, header, skip_prefixes, (prefix, suffix))

    def _loop_through_files_opt_out(self, re_ignore_patterns: List[Pattern]) -> None:
        base_dir = self.header_rc.work_path

        for root, _, files in os.walk(base_dir, topdown=True):
            file_path = os.path.join(root, root)
            file_path = os.path.relpath(file_path, base_dir)

            # Check if the current FOLDER matches any of the ignore patterns
            # This allows us to not go into that directory and save time
            if any(pattern.search(file_path) for pattern in re_ignore_patterns):
                if self.verbose and not file_path.startswith(".git"):
                    cprint(f"Skip - {file_path}", "yellow")
                continue

            for file in files:
                file_path = os.path.join(root, file)
                file_path = os.path.relpath(file_path, base_dir)
                # Check if the current FILE matches any of the ignore patterns
                if any(pattern.search(file_path) for pattern in re_ignore_patterns):
                    if self.verbose and not file_path.startswith(".git"):
                        cprint(f"Skip - {file_path}", "yellow")
                    continue

                full_file_path = Path(base_dir / file_path)
                if not full_file_path.is_file():
                    if self.verbose and not file_path.startswith(".git"):
                        cprint(f"Skip (not a file) - {file_path}", "yellow")
                    continue

                rel_file_path = Path(file_path)

                header, prefix, suffix, success = self.header_rc.get_header_for_file(file)
                if success:
                    if str(self.header_action) == str(Header_Action.REMOVE):
                        self._remove_header_from_file(full_file_path, rel_file_path, header)
                    elif str(self.header_action) == str(Header_Action.ADD):
                        skip_prefixes = self.header_rc.get_skip_lines_that_start_for_file(file)
                        self._add_header_to_file(full_file_path, rel_file_path, header, skip_prefixes, (prefix, suffix))


def _get_bool(config: dict[str, Any], input_str: str, default=False) -> bool:
    if str(config.get(input_str, default)).lower() == "true":
        return True
    elif str(config.get(input_str, default)).lower() == "false":
        return False
    return default


def main(args=sys.argv[1:]) -> None:
    parser = argparse.ArgumentParser(
        description="Add header action",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
    )

    parser.add_argument("--dry-run", help="Don't actually change files, but output effected files instead.")
    parser.add_argument("--verbose", help="Add more output to the console for debugging.")
    parser.add_argument("--unit-test-mode", help="Only needed for unit test.")
    parser.add_argument(
        "--file-name", help="Use a different file name other than .headerrc.yml.", default=".headerrc.yml"
    )

    args, unknown = parser.parse_known_args(args)
    config = vars(args)  # Get args to print

    if unknown:
        print("Unknown arguments: ", unknown)

    # ? NOTE: - is replaced with _ in args
    dry_run = _get_bool(config, "dry_run")
    verbose = _get_bool(config, "verbose")
    unit_test_mode = _get_bool(config, "unit_test_mode", default=False)
    file_name = config.get("file_name", ".headerrc.yml")

    # Better to print
    args_detected = {
        "--dry-run": dry_run,
        "--verbose": verbose,
        "--file-name": file_name,
    }
    print("Arguments detected:", args_detected)

    h = HeaderPy(verbose=verbose, dry_run=dry_run, unit_test_mode=unit_test_mode, file_name=file_name)
    h.run()


if __name__ == "__main__":
    main()
