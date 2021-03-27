# goji

goji is a minimal command line client for JIRA.

## Installation

Installation on macOS using [Homebrew](https://brew.sh/):

```shell
$ brew install kylef/formulae/goji
```

Install goji using pip:

```shell
$ pip install goji
```

## Configuration

Once installed, goji requires the base URL of your Atlassian suite to be
configured to run commands. There are a few ways to configured goji.

### Configuration File

The `~/.config/goji/config.toml` file can be configured, by setting profiles
for different JIRA instances. For example:

```toml
[profile.default]
url = "https://goji.atlassian.net"
email = "kyle@fuller.li"
```

Then:

```shell
$  export GOJI_PASSWORD='my password'
$ goji whoami
```

### Without Configuration File


```bash
$ export GOJI_BASE_URL=https://example.atlassian.net
```

```bash
$ goji --base-url https://example.atlassian.net show GOJI-43
```

To authenticate, use the [`login`](#login) command. This step is required to use
the other commands:

```bash
$ goji login
```

To provide authentication only for the current command, you can pass email and
password as options:

```bash
$ goji --email kyle@example.com --password pass whoami
```

Or alternatively, you may set the credentials using environment variables.

```bash
$ export GOJI_EMAIL=kyle@example.com
$ export GOJI_PASSWORD=password
```

## Usage

Subcommands:

- [login](#login) - Authenticate with JIRA server
- [whoami](#whoami) - View information regarding current user
- [show](#show) - Show details about issue
- create - Create a new issue
- [assign](#assign) - Assign an issue to a user
- [unassign](#unassign) - Unassign a user from an issue
- [comment](#comment) - Comment on an issue
- [change-status](#change-status) - Change the status of an issue
- edit - Edit issue description
- attach - Attach file(s) to an issue
- [open](#open) - Open issue in a web browser
- [search](#search) - Search issues using JQL
- [sprint](#sprint) - Collection of commands to manage sprints

### login

Authenticate with a JIRA server.

```bash
$ goji login

Email: delisa@example.com
Password:
```

### show

Show detailed information about an issue.

```bash
$ goji show GOJI-1
-> GOJI-1
  As a user, I would like to view an issue status

  - Status: Closed
  - Creator: Kyle Fuller (kylef)
  - Assigned: Kyle Fuller (kylef)
  - URL: https://cocode.atlassian.net/browse/GOJI-1

  Related issues:
  - Relates to: GOJI-2 (Closed)
```

### open

Opens an issue in your browser.

```bash
$ goji open GOJI-1
```

### assign / unassign

Assigns yourself or another user to an issue.

```bash
$ goji assign GOJI-1
You have been assigned to GOJI-1.
$ goji assign GOJI-1 sam
sam has been assigned to GOJI-1.
$ goji unassign GOJI-1
GOJI-1 has been unassigned.
```

### comment

Add a comment to an issue, editing text in your `$EDITOR`

```bash
$ goji comment GOJI-1
```

### search

Search issues using
[JQL](https://confluence.atlassian.com/jiracoreserver073/advanced-searching-861257209.html)

```bash
$ goji search "project=GOJI AND assignee=sam"
GOJI-21 Update core metrics
GOJI-40 Remove expired food from fridge
```

### change-status

Change the status of an issue

```bash
$ goji change-status GOJI-311 "done"
Fetching possible transitions...
Okay, the status for GOJI-311 is now "Done".
```

```bash
$ goji change-status GOJI-311
Fetching possible transitions...
0: To Do
1: In Progress
2: Done
Select a transition: 1
Okay, the status for GOJI-311 is now "In Progress".
```

### sprint

- create - Create a sprint

## License

goji is released under the BSD license. See [LICENSE](LICENSE).

