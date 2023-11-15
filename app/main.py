import os
import sys
from pathlib import Path
from re import Pattern
from typing import List, Optional, Union

from headerrc import HeaderRC


class HeaderPy:
    def __init__(self) -> None:
        self.header_rc = HeaderRC()

    def run(self):
        self._loop_through_files(self.header_rc.ignores)

    def _add_header_to_file(
        self,
        file_path: Union[Path, str],
        header: str,
        skip_prefixes: Optional[List[Pattern]] = None,
    ) -> None:
        if isinstance(file_path, str):
            file_path = Path(file_path)

        # Read the beginning of the file to check for the header
        header_bytes = sys.getsizeof(header) + 100

        with file_path.open("r+") as file:
            start_of_file = file.read(header_bytes)
            if header in start_of_file:
                return  # Header already present, no need to add it

            file.seek(0, 0)  # Rewind to start of the file for re-reading
            contents = file.read()  # Read the entire file
            lines = contents.split("\n")

            skip_index = 0
            if skip_prefixes:
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

            modified_content = (
                "\n".join(lines[:skip_index])
                + header_formatted
                + "\n".join(lines[skip_index:])
            )
            file.seek(0, 0)  # Move to the start of the file
            file.write(modified_content)  # Write the modified content
            file.truncate()  # Truncate in case the new content is shorter

    def _loop_through_files(self, re_ignore_patterns: List[Pattern]) -> None:
        base_dir = self.header_rc.work_path

        for root, _, files in os.walk(base_dir, topdown=True):
            file_path = os.path.join(root, root)
            file_path = os.path.relpath(file_path, base_dir)

            # Check if the current FOLDER matches any of the ignore patterns
            # This allows us to not go into that directory and save time
            if any(pattern.search(file_path) for pattern in re_ignore_patterns):
                continue

            for file in files:
                file_path = os.path.join(root, file)
                file_path = os.path.relpath(file_path, base_dir)

                # Check if the current FILE matches any of the ignore patterns
                if any(pattern.search(file_path) for pattern in re_ignore_patterns):
                    continue

                full_file_path = Path(base_dir / file_path)
                if not full_file_path.is_file():
                    continue

                relative_file_path = Path(file_path)

                print("Processing:", relative_file_path)

                header = self.header_rc.get_header_for_file(file)
                skip_prefixes = self.header_rc.get_skip_lines_that_start_for_file(file)

                self._add_header_to_file(full_file_path, header, skip_prefixes)


if __name__ == "__main__":
    h = HeaderPy()
    h.run()
