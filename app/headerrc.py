import re
from typing import List, Optional, Any
import yaml
import os
from re import Pattern
from pathlib import Path

# Set this enviornment variable and all the paths will be local (ie. not in a container)
TEST_MODE = os.getenv("TEST_MODE", False)


class HeaderRC:
    def __init__(self):
        self.home_path = Path("/action/workspace/")
        self.work_path = Path("/github/workspace")
        if TEST_MODE == "true" or TEST_MODE == True:
            print("--- Running in TEST mode ---")
            self.work_path = Path()
            self.home_path = Path()

        self.default_yml: Any
        self.user_yml: Any
        self._file_associations: dict = {}
        self.file_associations_by_comment: dict = {}
        self.file_associations_by_extension: dict = {}

        self._load_default_yml()
        self._load_user_yml()
        self.untrack_gitignore_enabled = self._get_untrack_gitignore_enabled()
        self.file_associations_by_comment = self._get_file_associations_by_comment()
        self.file_associations_by_extension = self._get_file_associations_by_extension()
        self._flatten_file_associations("file_associations_by_comment")
        self._flatten_file_associations("file_associations_by_extension")
        self._skip_lines_that_start_with_raw = (
            self._get_skip_lines_that_start_with_raw()
        )
        self.header = self._get_header()

        self.ignores: list[Pattern] = []
        self._load_ignores()

    def _load_default_yml(self):
        p = Path(self.home_path / "headerrc-default.yml")

        if not p.exists():
            print("ERROR: Could not find the default configuration file.")
            print("Valid locations are:")
            print(f" - {p}")
            exit(1)

        with open(p, "r") as file:
            self.default_yml = yaml.safe_load(file)

    def _load_user_yml(self):
        file_name = ".headerrc.yml"
        p = Path(self.work_path)
        p1 = p / f".github/{file_name}"
        p2 = p / f"{file_name}"

        if not p1.exists() and not p2.exists():
            print("ERROR: Could not find configuration file.")
            print("Valid locations are:")
            print(f" - {p1}")
            print(f" - {p2}")
            exit(1)

        if p1.exists():
            print(f"Found {p1}")
            with open(p1, "r") as file:
                self.user_yml = yaml.safe_load(file)

        if p2.exists():
            print(f"Found {p2}")
            with open(p2, "r") as file:
                self.user_yml = yaml.safe_load(file)
                
        if p1.exists() and p2.exists():
            print("WARNING: Found 2 configuration files.")
            print(f" - {p1}")
            print(f" - {p2}")
            print(f"WARNING {p2} will be used. All others are ignored")

    def _handle_untrack_gitignore(self):
        if not self.untrack_gitignore_enabled:
            return []

        patterns = []
        gitignore_path = os.path.join(self.work_path, ".gitignore")
        try:
            with open(gitignore_path, "r") as file:
                for line in file:
                    # Strip whitespace and skip empty lines and comments
                    stripped_line = line.strip()
                    if stripped_line and not stripped_line.startswith("#"):
                        # Convert the .gitignore pattern to a regex pattern
                        regex_pattern = re.escape(stripped_line).replace(r"\*", ".*")
                        patterns.append(re.compile(regex_pattern))
        except FileNotFoundError:
            print(f"No .gitignore file found at {gitignore_path}")
        return patterns

    def _load_ignores(self) -> list[Pattern]:
        ignores1 = set(list(self.default_yml.get("untracked_files", [])))
        ignores2 = set(list(self.user_yml.get("untracked_files", [])))
        ignores1.update(ignores2)
        ignores = list(ignores1)

        ignores_to_remove = []
        ignores_filtered = []
        for ig in ignores:
            if ig.startswith("!") and ig[1:] in ignores:
                ignores_to_remove.append(ig[1:])
                continue
            ignores_filtered.append(ig)

        for ig in ignores_to_remove:
            ignores_filtered.remove(ig)

        for pattern in ignores_filtered:
            p = re.compile(rf"{pattern}")
            self.ignores.append(p)

        gitignore = self._handle_untrack_gitignore()
        self.ignores += gitignore
        return self.ignores

    def _flatten_file_associations(self, yml_tag_name: str) -> dict:
        """Flatten file associations for faster processing"""

        if yml_tag_name == "file_associations_by_comment":
            file_associations_by_comment = self.file_associations_by_comment
            for k, v in file_associations_by_comment.items():
                if isinstance(v, list):
                    for ext in v:
                        self._file_associations[ext] = k
                else:
                    print(f"Unknown fileassociations {k}, {v}")

        elif yml_tag_name == "file_associations_by_extension":
            file_associations_by_extension = self.file_associations_by_extension
            for k, v in file_associations_by_extension.items():
                if isinstance(v, list):
                    for ext in v:
                        self._file_associations[k] = v
                elif isinstance(v, str):
                    self._file_associations[k] = v
        else:
            print(f"Unknown yml_tag_name '{yml_tag_name}'")
        return self._file_associations

    def get_header_for_file(self, file_path: str) -> str:
        prefix = ""
        suffix = ""
        for pattern, val in self.file_associations_regex.items():
            if pattern.search(file_path):
                if isinstance(val, list):
                    # If it is a list, allow for prefix and suffix
                    if len(val) == 1:
                        prefix = val[0]
                    elif len(val) == 2:
                        prefix = val[0]
                        suffix = val[1]
                    elif len(val) == 0:
                        pass
                    else:
                        print(f"Invlaid pattern for '{val}': {pattern.pattern}")
                elif isinstance(val, str):
                    # If it is a string, assume only the prefix
                    prefix = val
                else:
                    print(f"Invlaid pattern for '{val}': {pattern.pattern}")

                break
        else:
            return ""

        new_header = ""
        for line in self.header.splitlines(keepends=False):
            if line.strip() != "":
                new_header += f"{prefix} {line} {suffix}\n"

        return new_header

    def _dict_to_regex(self, dict_input: dict) -> dict[Pattern, str]:
        new_dict: dict[Pattern, str] = {}
        for k, v in dict_input.items():
            new_kew = re.compile(rf"{k}")
            new_dict[new_kew] = v

        return new_dict

    def get_skip_lines_that_start_for_file(self, file_path: str) -> Optional[List[Pattern]]:
        for pattern, val in self.skip_lines_that_start_with_regex.items():
            if pattern.search(file_path):
                if isinstance(val, list):
                    new_vals: List[Pattern] = []
                    for v in val:
                       new_vals.append(re.compile(rf"{v}"))
                    return new_vals
                elif isinstance(val, str):
                    return [re.compile(rf"{val}")]

                break
        return None

    def _get_untrack_gitignore_enabled(self) -> bool:
        val1 = self.default_yml.get("untrack_gitignore", None)
        val2 = self.user_yml.get("untrack_gitignore", None)

        if val2 is not None:
            return val2
        if val1 is not None:
            return val1

        return True  # Default value

    @property
    def file_associations_regex(self) -> dict[Pattern, str]:
        return self._dict_to_regex(self.file_associations)

    @property
    def file_associations(self) -> dict:
        return self._file_associations

    @property
    def skip_lines_that_start_with_regex(self) -> dict[Pattern, str]:
        return self._dict_to_regex(self._skip_lines_that_start_with_raw)

    def _get_file_associations_by_extension(self) -> dict:
        d1 = dict(self.default_yml.get("file_associations_by_extension", {}))
        d2 = dict(self.user_yml.get("file_associations_by_extension", {}))

        d1.update(d2)  # Merge the dictionaries
        return d1

    def _get_file_associations_by_comment(self) -> dict:
        d1 = dict(self.default_yml.get("file_associations_by_comment", {}))
        d2 = dict(self.user_yml.get("file_associations_by_comment", {}))

        d1.update(d2)  # Merge the dictionaries
        return d1

    def _get_skip_lines_that_start_with_raw(self) -> dict:
        d1 = dict(self.default_yml.get("skip_lines_that_start_with", {}))
        d2 = dict(self.user_yml.get("skip_lines_that_start_with", {}))

        d1.update(d2)  # Merge the dictionaries
        return d1

    def _get_header(self) -> str:
        h1 = str(self.default_yml.get("header", ""))
        h2 = str(self.user_yml.get("header", ""))

        if not h2:
            return h1
        return h2
