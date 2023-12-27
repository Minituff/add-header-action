<!-- SUPER SECRET CONFIDENTIAL -->
<!-- [2023] - [Infinity and Beyond] ACME CO -->
<!-- All Rights Reserved. -->
<!-- NOTICE: This is super secret info that -->
<!-- must be protected at all costs. -->

# Add header-action
[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-active-undefined.svg?logo=github&logoColor=white&style=flat)](https://github.com/marketplace/actions/add-header)
[![CI Status](https://github.com/Minituff/add-header-action/actions/workflows/lint-and-test.yml/badge.svg)](https://github.com/Minituff/add-header-action/actions/workflows/lint-and-test.yml)
[![codecov](https://codecov.io/github/Minituff/add-header-action/graph/badge.svg?token=NGVZKMXTM2)](https://codecov.io/github/Minituff/add-header-action)

Intelligently add a header to any file within your repo.

## Header examples
<details open><summary>------ Expand Me ------</summary>

This action can support any `UTF-8` file type.

**Bash**
```bash
#!/usr/bin/env bash

# SUPER SECRET CONFIDENTIAL 
# [2023] - [Infinity and Beyond] ACME Inc 
# All Rights Reserved. 

hello-world() {
    echo "Hello world"
}
```
**Javascript**
```js
// SUPER SECRET CONFIDENTIAL 
// [2023] - [Infinity and Beyond] ACME Inc 
// All Rights Reserved. 

function helloWorld() {
    console.log("Hello world")
}
```

**HTML**
```html
<!DOCTYPE html>

<!-- SUPER SECRET CONFIDENTIAL -->
<!-- [2023] - [Infinity and Beyond] ACME Inc -->
<!-- All Rights Reserved. -->

<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <link rel="stylesheet" href="style.css" type="text/css">
</head>
```

And many more.
</details>

## Usage
This action is ready to go out of the box. To change the header, see the [Customization](#customization) section.


```yml
name: Add header

jobs:
  build:
    name: Add headers
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
      with:
        token: ${{ secrets.PAT }} # (only needed for private repos)
    
    - name: Add header action step
      uses: minituff/add-header-action@v1
      with: # All arguments are optional, see the defaults below
        dry-run: false # Don't make any changes, but log what *would* change.
        verbose: false # Extra logging to help you debug.
        file-name: .headerrc.yml # The name of your settings file.
      env:
        FORCE_COLOR: "1" # Optional: Shows color output in GitHub console.

    - name: Commit and Push changes back to repo
      uses: stefanzweifel/git-auto-commit-action@v5
```
## Customization
Create a `.headerrc.yml` file in either the `.github` **or** *root* diretory of your project.

```console
📦root
 ┣ 📂.github
 ┃ ┣ 📂workflows
 ┃ ┃ ┗ 📜add-header-workflow.yml
 ┃ ┗ 📜.headerrc.yml             # <---- Either here
 ┗ 📜.gitignore

📦root
 ┣ 📜.headerrc.yml               # <---- Or here
 ┗ 📜.gitignore
```

This action loads default values from the [headerrc-default.yml](/headerrc-default.yml) <small>(this is built into the action)</small>, then merges them with the values from the [.headerrc.yml](/.github/.headerrc.yml) file from your repo.

The following are a list of configurable options in the `.headerrc.yml`:

```yaml
# Choose what to do with the header.
# remove  =  Remove an existing header from matching files.
# add     =  Add the header to any matching files.
header_action: add # Default: add

# Decide the method for choosing which files to add headers to.
# opt-out  =  all files will be selected unless the file path matches untracked_files.
# opt-in   =   no files will be selected unless the file path matches anything in tracked_files.
file_mode: opt-out # Default: opt-out

# A list of regex used to match file paths to receive the header. (opt-in mode only)
tracked_files: 
  - ^README.md$

# A list of regex used to match file paths to be skipped. (opt-out mode only)
# All file paths *not* matched will receive a header.
untracked_files:
  - app/
  - ^Dockerfile$

# Automatically add everything in the .gitignore file into the untracked_files section.
# This can save lots of time because most of these files can be ignored.  (opt-out mode only)
untrack_gitignore: true # Default: true

use_default_file_settings: true # Default: true

# The header to be added. Do not add the comment (#, //) here, see the file_associations section for that.
header: |
  SUPER SECRET CONFIDENTIAL

  [2023] - [Infinity and Beyond] ACME Inc
  All Rights Reserved.
  
  NOTICE: This is super secret info that
  must be protected at all costs.

# Customize the negation character. See below for how to use this.
# Any *default* file assocation that has this character at the beginning of the (key/value) will be removed. This only works if it is matched exactly. 
negate_characters: "!" # Default: "!"

# Group mulitple items by the comment value.
file_associations_by_comment:
  "#": 
    - "^.gitignore$"
    - "!^.gitignore$" # <-- Negate default items like this
    - ".gitignore$" # <---- You can also re-add any negated items
  "//": 
    - ".js$"
    - ".ts$"

# The item extension and the assocated comment. Overrides file_associations_by_comment if duplicates.
# Remember the escape charter for yml is "\"
# Here, you can only negate items by their key
file_associations_by_extension:
  ".*\.ya?ml$": "#"
  "!.md": ["<!--", "-->"] # <--- Negate default items like this

# For files that have 'important' first lines (like bash), use this setting to move the header below that line.
# Here, you can only negate items by their key.
skip_lines_that_have:
  ".sh$": ["#!"]
```

## Understanding Negation
This action comes pre-loaded with many common files types in the [headerrc-default.yml](/headerrc-default.yml).
However, some of these file types may be incorrect for your project. To fix this, we allow *negation* of default items.


To negate something, the format is `<negate_characters><item headerrc-default.yml>`.

For example, we filter out the `.gitignore` in the [headerrc-default.yml](/headerrc-default.yml)
```yml
untracked_files:
  - ^\.gitignore
```
But if you would like to remove this item from the `untracked_files`. Simply add it to your `.headerrc.yml` with the `negation_characters` as the prefix.
It must match EXACTLY with is in the in the [headerrc-default.yml](/headerrc-default.yml).

```yml
untracked_files:
  - !^\.gitignore  <-- Negate ^\.gitignore
```

You can also change the negate_characters to be anything you'd like if the default clashes with your regex.
```yml
negate_characters: "++" # Default "!"
```

### What can be negated?

1. `tracked_files`
1. `untracked_files`
1. `file_associations_by_comment`
1. `file_associations_by_extension`
1. `skip_lines_that_have`

Negation is an easy to to remove the default settings, but if we have a file association wrong, please submit an Issue or PR so we can fix it for everyone.


## Default argumnet values

If your choose not to set any arguments in your GitHub workflows, they will take the following values:
```yml
dry-run: false 
verbose: false
file-name: .headerrc.yml # Located in either the `.github` or *root* diretory of your project.
```

## Developing & Contributing
Pull Requests are welcome. 
See the [DevContainer folder](/.devcontainer/README.md) for more information
