import jmespath
import logging


def evaluate_query(report, query):
    """
    Evaluate a JMESPath query against a report to determine if a device is compliant with a policy.
    
    Args:
        report: Dictionary containing parsed Lynis report data
        query: JMESPath query expression (e.g., "hardening_index > `70`", "os == 'Linux'")
    
    Returns:
        bool: True if query matches, False if it doesn't, None if evaluation failed
    """
    try:
        # Compile the JMESPath expression
        expression = jmespath.compile(query)
        
        # Execute the query against the report
        result = expression.search(report)
        
        # JMESPath returns the query result; convert to boolean
        # For boolean expressions, result will be True/False
        # For other expressions, convert truthy/falsy to bool
        if isinstance(result, bool):
            return result
        
        # Convert truthy/falsy values to boolean
        # None, empty strings, 0, empty lists are False
        # Everything else is True
        return bool(result)
        
    except jmespath.exceptions.JMESPathError as e:
        logging.error(f'Invalid JMESPath query "{query}": {e}')
        return None
    except Exception as e:
        logging.error(f'Unexpected error evaluating query "{query}": {e}', exc_info=True)
        return None
