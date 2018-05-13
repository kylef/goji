# GOJI Changelog

## Master

### Enhancements

- `goji search` accepts a format string to render the results. You can pass
  `--format` with a custom format for example `{key}`.
- `goji comment` can accept a comment message via `--message` or `-m` options.

### Bug Fixes

- Underlying JIRA Errors are now exposed to the command line interface.
- `goji show` will now show the correct inbound name for link inbound relations
