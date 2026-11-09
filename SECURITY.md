# Security Policy

This project is a small local command-line tool. It does not phone home and does not require an API key.

## Reporting a vulnerability

Please open a [GitHub issue](https://github.com/perron/skilleval/issues) and mention that it is a security report. Do not include secrets, tokens, or private file contents in the issue.

If the report includes a working exploit against this tool, describe the impact and a minimal reproduction without pasting live credentials.

## Notes for this tool

skilleval runs the solver command you give it, with a temporary working directory and a few environment variables. Treat the solver the same way you would any local script: it can do anything your user can do. This first release has no LLM judge and does not call an API.

## Supported versions

The `master` branch and the latest tagged release, when one exists, are supported.
