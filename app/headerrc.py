import re
from typing import List, Optional, Any
import yaml
import os
from re import Pattern
from pathlib import Path
from termcolor import cprint
from enum import Enum

# Set this enviornment variable and all the paths will be local (ie. not in a container)
DEV_MODE = os.getenv("DEV_MODE", "false")


class File_Mode(Enum):
    OPT_OUT = 1  # Default
    OPT_IN = 2


class HeaderRC:
    def __init__(self, verbose=False, unit_test_mode=False, use_default_paths=True) -> None:
        self.verbose = verbose
        self.home_path = Path("/app/")
        self.work_path = Path("/github/workspace")
        if str(DEV_MODE).lower() == "true" or unit_test_mode == True:
            if unit_test_mode is False:
                cprint("--- Running in DEV_MODE mode ---", "yellow")
            if use_default_paths is True:
                self.work_path = Path()
                self.home_path = Path()

        self.default_yml: Any = self._load_default_yml()
        self.user_yml: Any = self._load_user_yml()
        self._file_associations: dict = {}
        self.file_associations_by_comment: dict = {}
        self.file_associations_by_extension: dict = {}

        self.negate_characters: str = self._get_negate_characters()
        self.use_default_file_settings: bool = self._get_use_default_file_settings()
        self.untrack_gitignore = self._get_untrack_gitignore()
        self.file_associations_by_comment = self._get_file_associations_by_comment()
        self.file_associations_by_extension = self._get_file_associations_by_extension()
        self._flatten_file_associations("file_associations_by_comment")
        self._flatten_file_associations("file_associations_by_extension")
        self._skip_lines_that_have_raw = self._get_skip_lines_that_have_raw()

        self.header = self._get_header()

        self.file_mode: File_Mode = self._get_file_mode()

        self.ignores: list[Pattern] = []
        self.ignores_str: list[str] = []
        if self.file_mode == File_Mode.OPT_OUT:
            self._load_ignores()

        self.accepts: list[Pattern] = []
        self.accepts_str: list[str] = []
        if self.file_mode == File_Mode.OPT_IN:
            self._load_accepts()

        self._print_verbose()

    def _print_verbose(self):
        if not self.verbose:
            return
        # :nocov:

        cprint("Header:", "magenta")
        cprint(self.header, "green")
        print("")

        if self.file_mode == File_Mode.OPT_OUT:
            cprint("File-mode: ", "magenta", end="")
            cprint("opt-out\n", "green")

        if self.file_mode == File_Mode.OPT_IN:
            cprint("File-mode: ", "magenta", end="")
            cprint("opt-in\n", "green")

        cprint("Negate characters: ", "magenta", end="")
        cprint(f"{str(self.negate_characters)}\n", "green")

        cprint("Use default file settings: ", "magenta", end="")
        cprint(f"{str(self.use_default_file_settings)}\n", "green")

        cprint("File associations:", "magenta")
        cprint(str(self._file_associations), "green")
        print("")

        if self.file_mode == File_Mode.OPT_OUT:
            cprint("Untracked (blacklisted) files:", "magenta")
            cprint(f"{str(self.ignores_str)}\n", "green")

        if self.file_mode == File_Mode.OPT_IN:
            cprint("Tracked (whitelisted) files:", "magenta")
            cprint(f"{str(self.accepts_str)}\n", "green")

        cprint("Skip lines that have:", "magenta")
        cprint(str(self._skip_lines_that_have_raw), "green")
        # :nocov:

    def _load_default_yml(self):
        p = Path(self.home_path / "headerrc-default.yml")
        print("headerrc-default.yml PATH = ", p.absolute())

        if not p.exists():
            print("ERROR: Could not find the default configuration file.")
            print("Valid locations are:")
            print(f" - {p}")
            exit(1)

        with open(p, "r") as file:
            return yaml.safe_load(file)

    def _load_user_yml(self):
        file_name = ".headerrc.yml"
        p = Path(self.work_path)
        p1 = p / f".github/{file_name}"
        p2 = p / f"{file_name}"

        user_yml = {}

        if not p1.exists() and not p2.exists():
            print("ERROR: Could not find configuration file.")
            print("Valid locations are:")
            print(f" - {p1}")
            print(f" - {p2}")
            exit(1)

        if p1.exists():
            with open(p1, "r") as file:
                user_yml = yaml.safe_load(file)

        if p2.exists():
            with open(p2, "r") as file:
                user_yml = yaml.safe_load(file)

        if p1.exists() and p2.exists():
            print("WARNING: Found 2 configuration files.")
            print(f" - {p1}")
            print(f" - {p2}")
            print(f"WARNING {p2} will be used. All others are ignored")

        return user_yml

    def _handle_untrack_gitignore(self):
        if not self.untrack_gitignore:
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
                        self.ignores_str.append(stripped_line)
                        patterns.append(re.compile(regex_pattern))
        except FileNotFoundError:
            print(f"No .gitignore file found at {gitignore_path}")
        return patterns

    def _load_ignores(self) -> list[Pattern]:
        ignores1 = self.default_yml.get("untracked_files", [])
        if ignores1 is None or self.use_default_file_settings is False:
            ignores1 = []
        ignores1 = set(list(ignores1))

        ignores2 = self.user_yml.get("untracked_files", [])
        if ignores2 is None:
            ignores2 = []
        ignores2 = set(list(ignores2))

        ignores1.update(ignores2)
        ignores = list(ignores1)

        ignores_to_remove = []
        ignores_filtered = []
        for ig in ignores:
            if ig.startswith(self.negate_characters) and ig[1:] in ignores:
                ignores_to_remove.append(ig[1:])
                continue
            ignores_filtered.append(ig)

        for ig in ignores_to_remove:
            ignores_filtered.remove(ig)

        for pattern in ignores_filtered:
            p = re.compile(rf"{pattern}")
            self.ignores.append(p)
            self.ignores_str.append(pattern)

        gitignore = self._handle_untrack_gitignore()
        self.ignores += gitignore
        return self.ignores

    def _load_accepts(self) -> list[Pattern]:
        accepts1 = self.default_yml.get("tracked_files", [])
        if accepts1 is None or self.use_default_file_settings is False:
            accepts1 = []
        accepts1 = set(list(accepts1))

        accepts2 = self.user_yml.get("tracked_files", [])
        if accepts2 is None:
            accepts2 = []
        accepts2 = set(list(accepts2))

        accepts1.update(accepts2)
        accepts = list(accepts1)

        accepts_to_remove = []
        accepts_filtered = []
        for ac in accepts:
            if ac.startswith(self.negate_characters) and ac[1:] in accepts:
                accepts_to_remove.append(ac[1:])
                continue
            accepts_filtered.append(ac)

        for ac in accepts_to_remove:
            accepts_filtered.remove(ac)

        for pattern in accepts_filtered:
            p = re.compile(rf"{pattern}")
            self.accepts.append(p)
            self.accepts_str.append(pattern)

        return self.accepts

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

    def get_header_for_file(self, file_path: str) -> tuple[str, str, str, bool]:
        """Reuturns the (header, prefix, suffix) for the file path"""
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
            if self.verbose:
                cprint(f"No file assocation - {file_path}", "red")
            return "", "", "", False

        new_header = ""
        for line in self.header.splitlines(keepends=False):
            if line.strip() != "":
                new_header += f"{prefix} {line} {suffix}\n"

        return new_header, prefix, suffix, True

    def _dict_to_regex(self, dict_input: dict) -> dict[Pattern, str]:
        new_dict: dict[Pattern, str] = {}
        for k, v in dict_input.items():
            new_kew = re.compile(rf"{k}")
            new_dict[new_kew] = v

        return new_dict

    def get_skip_lines_that_start_for_file(self, file_path: str) -> Optional[List[Pattern]]:
        for pattern, val in self.skip_lines_that_have_regex.items():
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

    def _merge_dict_filter_key(self, d1: dict, d2: dict) -> None:
        # Prepare a set to track keys that should be removed
        removal_set = set()

        # Identify keys in d2 starting with '!' and add their counterparts to the removal set
        for key in d2:
            if key.startswith(self.negate_characters):
                removal_set.add(key.lstrip(self.negate_characters))

        # Remove identified keys from d1
        for key in list(d1):  # Use list to avoid 'dictionary changed size during iteration' error
            if key in removal_set:
                del d1[key]

        # Merge d2 into d1, excluding keys that start with "!"
        for key, values in d2.items():
            if not key.startswith(self.negate_characters):
                if key in d1:
                    if not isinstance(d1[key], list):
                        d1[key] = [d1[key]]
                    d1[key].extend(val for val in values)
                else:
                    d1[key] = values

    def _merge_dict_filter_val(self, d1: dict, d2: dict) -> None:
        # Prepare a set to track values that should be removed
        removal_set = set()

        # Identify values in d2 starting with '!' and add their counterparts to the removal set
        for values in d2.values():
            removal_set.update(
                val.lstrip(self.negate_characters) for val in values if val.startswith(self.negate_characters)
            )

        # Remove identified values from d1
        for key in d1:
            if key in d2:
                d1[key] = [val for val in d1[key] if val not in removal_set]

        # Merge d2 into d1, excluding values that start with "!"
        for key, values in d2.items():
            filtered_values = [val for val in values if not val.startswith(self.negate_characters)]
            if key in d1:
                if not isinstance(d1[key], list):
                    d1[key] = [d1[key]]
                d1[key].extend(val for val in filtered_values if val not in removal_set)
            else:
                d1[key] = filtered_values

    def _get_file_associations_by_extension(self) -> dict:
        d1 = dict(self.default_yml.get("file_associations_by_extension", {}))
        d2 = dict(self.user_yml.get("file_associations_by_extension", {}))
        if self.use_default_file_settings is False:
            d1 = {}  # Empty the default settings

        self._merge_dict_filter_key(d1, d2)  # Merge the dictionaries
        return d1

    def _get_file_associations_by_comment(self) -> dict:
        d1 = dict(self.default_yml.get("file_associations_by_comment", {}))
        d2 = dict(self.user_yml.get("file_associations_by_comment", {}))
        if self.use_default_file_settings is False:
            d1 = {}  # Empty the default settings

        self._merge_dict_filter_val(d1, d2)  # Merge the dictionaries
        return d1

    def _get_skip_lines_that_have_raw(self) -> dict:
        d1 = dict(self.default_yml.get("skip_lines_that_have", {}))
        d2 = dict(self.user_yml.get("skip_lines_that_have", {}))
        if self.use_default_file_settings is False:
            d1 = {}  # Empty the default settings

        self._merge_dict_filter_key(d1, d2)  # Merge the dictionaries
        return d1

    def _get_file_mode(self) -> File_Mode:
        f1 = str(self.default_yml.get("file_mode", ""))
        f2 = str(self.user_yml.get("file_mode", ""))
        if f1:
            if f1 == "opt-out":
                return File_Mode.OPT_OUT
            elif f1 == "opt-in":
                return File_Mode.OPT_IN

        if f2 == "opt-out":
            return File_Mode.OPT_OUT
        elif f2 == "opt-in":
            return File_Mode.OPT_IN
        elif f2 == "":
            return File_Mode.OPT_OUT

        return File_Mode.OPT_OUT

    def _get_untrack_gitignore(self) -> bool:
        val1 = self.default_yml.get("untrack_gitignore", True)
        val2 = self.user_yml.get("untrack_gitignore", None)

        if val2 is not None:
            return val2
        return val1

    def _get_use_default_file_settings(self) -> bool:
        b1 = self.default_yml.get("use_default_file_settings", True)
        b2 = self.user_yml.get("use_default_file_settings", None)

        if b2 is not None:
            return b2
        return b1

    def _get_negate_characters(self) -> str:
        n1 = self.default_yml.get("negate_characters", "!")
        n2 = self.user_yml.get("negate_characters", None)

        if n2 is not None:
            return n2
        return n1

    def _get_header(self) -> str:
        h1 = str(self.default_yml.get("header", ""))
        h2 = str(self.user_yml.get("header", ""))

        if not h2:
            return h1
        return h2

    @property
    def file_associations_regex(self) -> dict[Pattern, str]:
        return self._dict_to_regex(self.file_associations)

    @property
    def file_associations(self) -> dict:
        return self._file_associations

    @property
    def skip_lines_that_have_regex(self) -> dict[Pattern, str]:
        return self._dict_to_regex(self._skip_lines_that_have_raw)
