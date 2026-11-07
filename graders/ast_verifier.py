"""Abstract syntax tree and token-graph invariant checkers for code verification."""

import ast
import re
from typing import Any, List, Optional, Set

class AstInvariantChecker:
    """Provides structural static analysis on generated Python or pseudo-kernel code."""

    @staticmethod
    def extract_code_block(raw_text: str, default_language: str = "python") -> str:
        """Extracts code enclosed within markdown triple backticks or returns cleaned text.

        Args:
            raw_text: Raw output string from an LLM.
            default_language: Expected language label, defaults to python.

        Returns:
            str: Extracted and trimmed code block.
        """
        pattern = rf"```(?:{default_language})?\s*\n(.*?)\n```"
        matches = re.findall(pattern, raw_text, re.DOTALL | re.IGNORECASE)
        if matches:
            return matches[0].strip()
        generic_pattern = r"```\s*\n(.*?)\n```"
        generic_matches = re.findall(generic_pattern, raw_text, re.DOTALL)
        if generic_matches:
            return generic_matches[0].strip()
        return raw_text.strip()

    @staticmethod
    def parse_python_ast(source_code: str) -> Optional[ast.AST]:
        """Safely parses Python source string into an AST.

        Args:
            source_code: Python code to parse.

        Returns:
            Optional[ast.AST]: Parsed AST tree or None if syntax is invalid.
        """
        try:
            return ast.parse(source_code)
        except SyntaxError:
            return None

    @staticmethod
    def contains_function_call(tree: ast.AST, func_name: str) -> bool:
        """Determines if the AST contains a call to the specified function name.

        Args:
            tree: Parsed AST tree.
            func_name: Target function name to identify.

        Returns:
            bool: True if call node exists, False otherwise.
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == func_name:
                    return True
                elif isinstance(node.func, ast.Attribute) and node.func.attr == func_name:
                    return True
        return False

    @staticmethod
    def contains_keywords(source_code: str, required_keywords: List[str]) -> bool:
        """Checks if all required invariant tokens exist in the source code.

        Args:
            source_code: Source string.
            required_keywords: Tokens that must be present.

        Returns:
            bool: True if all tokens exist, False otherwise.
        """
        lower_code = source_code.lower()
        return all(kw.lower() in lower_code for kw in required_keywords)

    @staticmethod
    def check_forbidden_tokens(source_code: str, forbidden_tokens: List[str]) -> List[str]:
        """Detects presence of forbidden or anti-pattern tokens in code.

        Args:
            source_code: Source string.
            forbidden_tokens: Anti-pattern tokens.

        Returns:
            List[str]: List of forbidden tokens detected.
        """
        lower_code = source_code.lower()
        return [tok for tok in forbidden_tokens if tok.lower() in lower_code]
