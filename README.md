# auto-example-env

A Python utility to generate `example.env` from your `.env` file for documentation purposes.

## Installation

```bash
pip install .
```

## Usage

```bash
# Generate example.env from .env in current directory
auto-example-env

# Specify custom input/output files
auto-example-env --input .env --output example.env
```

## Features

- Converts `export KEY=VALUE` to `export KEY=`
- Handles multiline quoted values (e.g., PEM certificates) by adding a comment above
- Skips keys marked with `# ignore` (case insensitive)
- Preserves comments and empty lines
- Always overwrites `example.env`

## Example

Given `.env`:

```
export API_KEY=secret
# ignore export SECRET=hidden
export CERT="-----BEGIN CERTIFICATE-----
...
-----END CERTIFICATE-----"
```

Generates `example.env`:

```
export API_KEY=
# Multiline value
export CERT=
```

