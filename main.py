import argparse
import os
import sys


def parse_env_lines(lines: list[str]) -> list[str]:
    """
    Parse lines from .env file and generate lines for example.env.

    Handles:
    - export KEY=VALUE -> export KEY=
    - Multiline quoted values -> "# Multiline value" comment above, then export KEY=
    - Skip lines with # ignore (case insensitive)
    - Preserve comments and empty lines
    """
    output = []
    in_multiline = False
    multiline_key = None

    for line in lines:
        stripped = line.rstrip()  # keep leading spaces but strip trailing

        if not stripped:
            output.append(line)
            continue

        # Check for # ignore (case insensitive)
        if "# ignore" in line.lower():
            continue

        if stripped.startswith("#"):
            # Preserve comments
            output.append(line)
            continue

        if in_multiline:
            # Continue until closing quote
            if '"' in stripped:
                in_multiline = False
                output.append("# Multiline value\n")
                output.append(f"export {multiline_key}=\n")
            continue

        # Look for export KEY=...
        if stripped.startswith("export "):
            parts = stripped.split("=", 1)
            if len(parts) == 2:
                key_part = parts[0].strip()
                value_part = parts[1].strip()
                if value_part.startswith('"') and not value_part.endswith('"'):
                    # Start of multiline
                    in_multiline = True
                    multiline_key = key_part.replace("export ", "")
                    continue
                else:
                    # Single line
                    output.append(f"{key_part}=\n")
            else:
                # Malformed export line, keep as is
                output.append(line)
        else:
            # Non-export lines, keep as is
            output.append(line)

    return output


def extract_key(line: str) -> str | None:
    """Extract the key from an export line."""
    stripped = line.strip()
    if stripped.startswith("export "):
        parts = stripped.split("=", 1)
        if len(parts) >= 1:
            key_part = parts[0].strip()
            return key_part.replace("export ", "")
    return None


def extract_key_value(line: str) -> tuple[str, str] | None:
    """Extract the key and value from an export line."""
    stripped = line.strip()
    if stripped.startswith("export "):
        parts = stripped.split("=", 1)
        if len(parts) >= 1:
            key_part = parts[0].strip()
            key = key_part.replace("export ", "")
            value = parts[1] if len(parts) > 1 else ""
            return (key, value)
    return None


def merge_with_existing_example(
    env_lines: list[str], example_lines: list[str]
) -> list[str]:
    """
    Merge parsed .env lines with existing example.env lines.
    Preserves placeholder values from example.env while using structure from .env.
    """
    # Build a map of keys to placeholder values from existing example.env
    example_values = {}
    for line in example_lines:
        kv = extract_key_value(line)
        if kv:
            key, value = kv
            example_values[key] = value

    # Process env lines and substitute placeholder values where available
    output = []
    in_multiline = False
    multiline_key = None

    for line in env_lines:
        # Use original line for output to preserve formatting
        stripped = line.rstrip()

        if not stripped:
            # Preserve blank lines
            output.append(line)
            continue

        if stripped.startswith("#"):
            # Preserve comments
            output.append(line)
            continue

        if in_multiline:
            if '"' in stripped:
                in_multiline = False
                output.append("# Multiline value\n")
                output.append(f"export {multiline_key}=\n")
            continue

        # Check if this is an export line
        if stripped.startswith("export "):
            parts = stripped.split("=", 1)
            if len(parts) >= 1:
                key_part = parts[0].strip()
                key = key_part.replace("export ", "")

                # Check if we have more parts (i.e., there's a value)
                if len(parts) == 2:
                    value_part = parts[1].strip()

                    if value_part.startswith('"') and not value_part.endswith('"'):
                        # Start of multiline
                        in_multiline = True
                        multiline_key = key
                        continue

                # Single line - check if we have a placeholder
                if key in example_values:
                    placeholder_value = example_values[key]
                    # Ensure placeholder ends with newline
                    if not placeholder_value.endswith("\n"):
                        placeholder_value += "\n"
                    output.append(f"export {key}={placeholder_value}")
                else:
                    output.append(f"export {key}=\n")
            else:
                output.append(line)
        else:
            output.append(line)

    return output


def create_example_env(input_path: str, output_path: str) -> bool:
    """Read input .env and write to output example.env"""
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' does not exist.", file=sys.stderr)
        return False

    with open(input_path, "r", encoding="utf-8") as f:
        env_lines = f.readlines()

    # Check if existing example.env exists and preserve placeholder values
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            example_lines = f.readlines()
        output_lines = merge_with_existing_example(env_lines, example_lines)
    else:
        output_lines = parse_env_lines(env_lines)

    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(output_lines)

    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate example.env from .env file, stripping values for documentation."
    )
    parser.add_argument(
        "--input", "-i", default=".env", help="Path to input .env file (default: .env)"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="example.env",
        help="Path to output example.env file (default: example.env)",
    )

    args = parser.parse_args()

    success = create_example_env(args.input, args.output)
    if success:
        print(f"Successfully generated '{args.output}' from '{args.input}'")
    else:
        sys.exit(1)

    return 0


if __name__ == "__main__":
    sys.exit(main())
