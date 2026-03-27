import unittest
import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from main import parse_env_lines, create_example_env, merge_with_existing_example


class TestParseEnvLines(unittest.TestCase):
    def test_single_line_export(self):
        lines = ["export API_KEY=secret123\n"]
        result = parse_env_lines(lines)
        self.assertEqual(result, ["export API_KEY=\n"])

    def test_comment_preserved(self):
        lines = ["# This is a comment\n"]
        result = parse_env_lines(lines)
        self.assertEqual(result, ["# This is a comment\n"])

    def test_ignore_line(self):
        lines = ["export SECRET=hidden # ignore\n"]
        result = parse_env_lines(lines)
        self.assertEqual(result, [])

    def test_multiline_placeholder(self):
        lines = [
            'export SSL_CERT="-----BEGIN CERTIFICATE-----\n',
            '-----END CERTIFICATE-----"\n',
        ]
        result = parse_env_lines(lines)
        self.assertEqual(result, ["# Multiline value\n", "export SSL_CERT=\n"])

    def test_blank_line_preserved(self):
        lines = ["\n"]
        result = parse_env_lines(lines)
        self.assertEqual(result, ["\n"])

    def test_multiple_blank_lines(self):
        """Test that multiple blank lines are preserved correctly"""
        lines = ["export KEY1=value1\n", "\n", "\n", "export KEY2=value2\n"]
        result = parse_env_lines(lines)
        self.assertEqual(result, ["export KEY1=\n", "\n", "\n", "export KEY2=\n"])

    def test_blank_lines_at_end(self):
        """Test blank lines at end of file"""
        lines = ["export KEY=value\n", "\n", "\n"]
        result = parse_env_lines(lines)
        self.assertEqual(result, ["export KEY=\n", "\n", "\n"])


class TestMergeWithExistingExample(unittest.TestCase):
    def test_preserve_placeholder_values(self):
        """Test that existing placeholder values in example.env are preserved"""
        env_lines = ["export API_KEY=real_secret\n", "export DB_URL=real_db_url\n"]
        example_lines = ["export API_KEY=your_api_key_here\n", "export DB_URL=\n"]

        result = merge_with_existing_example(env_lines, example_lines)

        self.assertEqual(
            result, ["export API_KEY=your_api_key_here\n", "export DB_URL=\n"]
        )

    def test_add_new_vars_from_env(self):
        """Test that new variables from .env are added with empty values"""
        env_lines = ["export NEW_VAR=new_value\n", "export OLD_VAR=old_value\n"]
        example_lines = ["export OLD_VAR=placeholder\n"]

        result = merge_with_existing_example(env_lines, example_lines)

        self.assertEqual(result, ["export NEW_VAR=\n", "export OLD_VAR=placeholder\n"])

    def test_remove_vars_not_in_env(self):
        """Test that variables not in .env are removed from example"""
        env_lines = ["export KEEP_VAR=keep_value\n"]
        example_lines = [
            "export KEEP_VAR=keep_placeholder\n",
            "export REMOVE_VAR=remove_placeholder\n",
        ]

        result = merge_with_existing_example(env_lines, example_lines)

        self.assertEqual(result, ["export KEEP_VAR=keep_placeholder\n"])

    def test_preserve_comments_and_structure(self):
        """Test that comments and structure are preserved from env file"""
        env_lines = [
            "# API Configuration\n",
            "export API_KEY=secret\n",
            "\n",
            "# Database\n",
            "export DB_URL=postgres://localhost\n",
        ]
        example_lines = [
            "export API_KEY=your_api_key\n",
            "export DB_URL=your_database_url\n",
        ]

        result = merge_with_existing_example(env_lines, example_lines)

        expected = [
            "# API Configuration\n",
            "export API_KEY=your_api_key\n",
            "\n",
            "# Database\n",
            "export DB_URL=your_database_url\n",
        ]
        self.assertEqual(result, expected)


class TestCreateExampleEnv(unittest.TestCase):
    def test_creates_example_when_no_existing(self):
        """Test creating example.env when none exists"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False
        ) as env_file:
            env_file.write("export API_KEY=secret\n")
            env_file.write("export DB_URL=postgres://localhost\n")
            env_path = env_file.name

        example_path = env_path.replace(".env", ".example.env")

        try:
            success = create_example_env(env_path, example_path)
            self.assertTrue(success)

            with open(example_path, "r") as f:
                content = f.read()

            self.assertIn("export API_KEY=\n", content)
            self.assertIn("export DB_URL=\n", content)
        finally:
            os.unlink(env_path)
            if os.path.exists(example_path):
                os.unlink(example_path)

    def test_preserves_existing_placeholders(self):
        """Test that existing example.env placeholders are preserved"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False
        ) as env_file:
            env_file.write("export API_KEY=new_secret\n")
            env_file.write("export NEW_VAR=new_value\n")
            env_path = env_file.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".example.env", delete=False
        ) as example_file:
            example_file.write("export API_KEY=your_api_key_here\n")
            example_file.write("export OLD_VAR=old_placeholder\n")
            example_path = example_file.name

        try:
            success = create_example_env(env_path, example_path)
            self.assertTrue(success)

            with open(example_path, "r") as f:
                content = f.read()

            # Should preserve placeholder
            self.assertIn("export API_KEY=your_api_key_here\n", content)
            # Should add new var with empty value
            self.assertIn("export NEW_VAR=\n", content)
            # Should remove old var not in .env
            self.assertNotIn("export OLD_VAR", content)
        finally:
            os.unlink(env_path)
            os.unlink(example_path)


if __name__ == "__main__":
    unittest.main()
