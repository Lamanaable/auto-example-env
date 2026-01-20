import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from main import parse_env_lines


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


if __name__ == "__main__":
    unittest.main()
