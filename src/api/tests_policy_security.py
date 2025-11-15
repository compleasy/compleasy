import pytest
from api.utils.policy_query import evaluate_query
from api.utils.lynis_report import LynisReport


@pytest.mark.security
class TestPolicyQuerySecurity:
    """Security tests for policy query evaluation using JMESPath."""
    
    @pytest.fixture
    def sample_report(self):
        """Create a sample report for testing."""
        report_data = """report_version_major=3
report_version_minor=0
hardening_index=75
automation_tool_running=ansible
"""
        lynis_report = LynisReport(report_data)
        parsed = lynis_report.get_parsed_report()
        # Convert numeric string fields to integers for proper comparison
        # In real reports, these are strings, but for testing we convert them
        if 'hardening_index' in parsed and parsed['hardening_index'].isdigit():
            parsed['hardening_index'] = int(parsed['hardening_index'])
        return parsed
    
    def test_sql_injection_attempts(self, sample_report):
        """Test that SQL injection patterns are safely rejected by JMESPath."""
        malicious_queries = [
            "hardening_index == `75`; DROP TABLE devices;",
            "automation_tool_running == 'test' OR '1'=='1'",
            "hardening_index == `75` UNION SELECT * FROM users",
            "contains(automation_tool_running, '\"; DELETE FROM licensekey; --')",
        ]
        
        for query in malicious_queries:
            # JMESPath will reject invalid syntax (semicolons, SQL keywords in wrong context)
            # This is safe because: 1) No SQL is executed, 2) JMESPath only parses valid expressions
            result = evaluate_query(sample_report, query)
            # JMESPath should reject these as invalid syntax, returning None
            # Or if it parses part of it, it should return bool/None (not execute SQL)
            assert isinstance(result, (bool, type(None))), f"Query should return bool or None: {query}"
    
    def test_code_injection_attempts(self, sample_report):
        """Test that code injection patterns are rejected by JMESPath."""
        malicious_queries = [
            "hardening_index == `__import__('os').system('ls')`",
            "contains(automation_tool_running, exec('print(1)'))",
            "hardening_index == `eval('1+1')`",
        ]
        
        for query in malicious_queries:
            # JMESPath will reject these as invalid syntax
            # Even if parsed, backticks create literals, not code execution
            result = evaluate_query(sample_report, query)
            # Should return None (invalid) or False (if somehow parsed as literal comparison)
            assert isinstance(result, (bool, type(None))), f"Code injection should be blocked: {query}"
    
    def test_path_traversal_attempts(self, sample_report):
        """Test that path traversal patterns are safely handled."""
        malicious_queries = [
            "contains(automation_tool_running, '../../../etc/passwd')",
            "hardening_index == `../../config`",
        ]
        
        for query in malicious_queries:
            result = evaluate_query(sample_report, query)
            # Should evaluate safely (not cause file access)
            # JMESPath only evaluates expressions, doesn't access filesystem
            assert isinstance(result, (bool, type(None)))
    
    def test_field_validation(self, sample_report):
        """Test that valid JMESPath queries work correctly."""
        valid_queries = [
            "hardening_index > `70`",
            "contains(automation_tool_running, 'ansible')",
            "hardening_index == `75`",
            "hardening_index >= `70` && hardening_index <= `80`",
        ]
        
        for query in valid_queries:
            result = evaluate_query(sample_report, query)
            assert result is not None, f"Valid query should return bool: {query}"
            assert isinstance(result, bool), f"Result should be boolean: {query}"
    
    def test_operator_validation(self, sample_report):
        """Test that invalid JMESPath operators are rejected."""
        invalid_queries = [
            "hardening_index << `75`",  # << not a valid JMESPath operator
        ]
        
        for query in invalid_queries:
            result = evaluate_query(sample_report, query)
            # JMESPath should reject invalid syntax
            assert result is None, f"Invalid operator should be rejected: {query}"
        
        # These queries are actually valid JMESPath syntax (they evaluate to truthy/falsy)
        # but they don't make logical sense for our use case
        valid_but_illogical_queries = [
            "hardening_index && `75`",  # This is valid but returns the right operand if left is truthy
            "automation_tool_running || test",  # This is valid but returns left if truthy, else right
        ]
        
        for query in valid_but_illogical_queries:
            result = evaluate_query(sample_report, query)
            # These are valid JMESPath, so they return a value (not None)
            # But they're not useful for boolean comparisons
            assert result is not None, f"Query is valid JMESPath but not useful: {query}"
    
    def test_resource_exhaustion(self, sample_report):
        """Test that long queries don't cause resource exhaustion."""
        # Test with very long query (long integer literal)
        long_query = "hardening_index == `" + "1" * 10000 + "`"
        result = evaluate_query(sample_report, long_query)
        # JMESPath should handle long literals without hanging
        # Result will be False (value doesn't match) or None (if parsing fails)
        assert isinstance(result, (bool, type(None))), "Parser should handle long integers"
        
        # Test with very long field name (should be rejected or handled safely)
        long_field_query = "a" * 10000 + " == `1`"
        result = evaluate_query(sample_report, long_field_query)
        assert isinstance(result, (bool, type(None))), "Parser should handle long field names"
    
    def test_complex_boolean_expressions(self, sample_report):
        """Test that complex boolean expressions work correctly."""
        complex_queries = [
            "hardening_index > `70` && hardening_index < `80`",
            "hardening_index > `80` || automation_tool_running == 'ansible'",
            "!(hardening_index < `50`)",
        ]
        
        for query in complex_queries:
            result = evaluate_query(sample_report, query)
            assert result is not None, f"Complex query should return bool: {query}"
            assert isinstance(result, bool), f"Result should be boolean: {query}"
