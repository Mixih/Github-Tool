# Gitbot

A very simple and hacky datasource to github organization synchronization tool.

## Supported Datasources/git hosts

**Data Sources**
- CSV spreadsheet

**Git Hosts**
- Github

## Installation

1. Download/clone this repo
2. Initialize new python 3 venv (replace python3 with python if the system python
   is python 3): `python3 -m venv [name of venv]`
3. Activate venv by using `. [name of venv]/bin/activate` (on windows, use
   powershell, install python3 to path, and type `. [name of
   venv]/Scripts/activate.ps1`
4. Install dependencies with `pip3 install -r requirements.txt`

## Usage

`python3 gitbot.py -c [name of username column] -t [github apikey] [CSV datafile] [organization]`

Additional options include:
- `--help` : print integrated help message
- `--name-fmt` : set the basename that the variable name column will be applied
    to (i.e. `my-basename{}-year` will replace the `{}` with the values of the
    specified name column
- `--name-col` : set the column that will be used to populate the repo names'
    format strings
- `--user-col` : set the columns of usernames that will be synced to the org
- `--team` : set the team that all users will be added to if they are not
    members already
- `--interactive` : forces the script to confirm all chagnes it will make before
    executing them

The git apikey supported  is a personal access token, which can be generated from
`Settings>Developer settings>Personal access tokens`. It can be passed from an
environment variable instead of being directly pasted on the command line to
prevent leaving it shell history. Just specify a variable of the form `$VARNAME`
and the script will automatically pull the value of that variable if it is
valid.

Note that the Github API key must have the following scopes:
- `repo` (whole scope)
- `admin:org` (whole scope)
Additionally the account where the token is generated must have `owner` or
`admin` permission on the organization to be managed for all features to work.
