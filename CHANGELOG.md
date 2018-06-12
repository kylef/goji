# GOJI Changelog

## Master

### Bug Fixes

- Prevents a potential problem when using JIRA with SSO instances which uses
  cookies. In some cases an invalid authorization header would be sent which
  doesn't affect the use of goji. However when authorization headers with bad
  credentials are sent in a request it causes a failed login in JIRA (even
  though the request actual succeeds).


## 0.3.0

### Enhancements

- `goji search` accepts a format string to render the results. You can pass
  `--format` with a custom format for example `{key}`.
- `goji comment` can accept a comment message via `--message` or `-m` options.

### Bug Fixes

- Underlying JIRA Errors are now exposed to the command line interface.
- `goji show` will now show the correct inbound name for link inbound relations
