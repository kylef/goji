# GOJI Changelog

## 0.7.0 (2025/04/12)

### Enhancements

- `goji edit` supports setting summary and custom fields on an issue.

- New `goji report` command allowing generation of HTML reports.

## 0.6.0 (2025/03/10)

### Enhancements

- `goji search` contains an `--all` option to view all issues (paginating
  through each page).
- Added `goji link` command to link two issues together.
- Add support for an undocumented and unstable plugin ecosystem to extend goji.

## 0.5.0

### Enhancements

- Profile can now be set with environment variable `GOJI_PROFILE`.
- `goji search` now has an `--count` option which returns amount of tickets
  matching search query.
- Search results now use hyperlinks for JIRA ticket keys.
- Performance improvement to search by only requesting desired fields from
  jira.
- New `goji comments` command for viewing comments for a ticket.

## 0.4.0

### Breaking Changes

- Issue type argument of `goji create` is not an option `--type/-t`.

### Enhancements

- `goji create` now accepts the `--label` option to supply labels.
- goji now allows you to provide authentication credentials using `--email` and
  `--password` options, or alternatively the `GOJI_EMAIL` and `GOJI_PASSWORD`
  environment variables.

- Support for profiles and configuration files.

## 0.3.1

### Bug Fixes

- Prevents a potential problem when using JIRA with SSO instances which uses
  cookies. In some cases an invalid authorization header would be sent which
  doesn't affect the use of goji. However when authorization headers with bad
  credentials are sent in a request it causes a failed login in JIRA (even
  though the request actual succeeds).

- Allows `goji create` to create a issues on some JIRA configurations where
  `components` is not a permitted field in the create issue screen.

- Makes `goji change-status` work on Python 3, this was causing problems due to
  Python 2/3 differences.


## 0.3.0

### Enhancements

- `goji search` accepts a format string to render the results. You can pass
  `--format` with a custom format for example `{key}`.
- `goji comment` can accept a comment message via `--message` or `-m` options.

### Bug Fixes

- Underlying JIRA Errors are now exposed to the command line interface.
- `goji show` will now show the correct inbound name for link inbound relations
