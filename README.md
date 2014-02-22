goji
====

[![Build Status](https://travis-ci.org/kylef/goji.png?branch=master)](https://travis-ci.org/kylef/goji)

goji is a minimal command line client for JIRA.

**NOTE**: This is in early development, not fully ready yet.

## Usage

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

## License

goji is released under the BSD license. See [LICENSE](LICENSE).
