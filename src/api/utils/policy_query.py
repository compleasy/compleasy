from pyparsing import Word, alphas, nums, oneOf, quotedString, ParseException, Suppress, Optional, Combine
import logging
from django.db.models import Q
from django.apps import apps
from utils.lynis_report import LynisReport

# Define the components of the query
word = Word(alphas + '_')
operator = oneOf("= != > < >= <= contains")
integer = Word(nums)
quoted_string = quotedString

# Combine the components into a condition with optional spaces
condition = word + Optional(Suppress(' ')) + operator + Optional(Suppress(' ')) + (integer | quoted_string)

def parse_query(query):
    """Parse the query string into its components."""
    try:
        parsed = condition.parseString(query)
        logging.debug('Parsed query components: %s', parsed)
        return parsed
    except ParseException as e:
        logging.error('ParseException: %s', e)
        return None

def evaluate_query(report, query):
    """Evaluate a query against a report to determine if a device is compliant with a policy."""
    """Query example: automation_tool_running contains "ansible" or hardening_index > 80"""
    parsed_query = parse_query(query)
    if not parsed_query or len(parsed_query) < 3:
        logging.error('Invalid query: %s', query)
        return None
    logging.debug('Parsed query: %s', parsed_query)

    # Get the field name and the operator
    field, operator, value = parsed_query
    logging.debug('Field: %s, operator: %s, value: %s', field, operator, value)

    # Remove quotes from the value if it's a quoted string
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    elif value.startswith("'") and value.endswith("'"):
        value = value[1:-1]

    # Get full report from report object and parse it using LynisReport class
    report_value = report.get(field)
    logging.debug('Report value: %s', report_value)

    if report_value is None:
        logging.error('Field not found in report: %s', field)
        return None

    if operator == 'contains':
        # If the field is a string, check if the value is in the string
        if not isinstance(value, str):
            logging.error('Query value is not a string: %s', value)
            return None
        
        # If the field is a string or list, check if the value is in the string or list
        if isinstance(report_value, str) or isinstance(report_value, list):
            logging.debug('Checking if %s contains %s', report_value, value)
            logging.debug('RESULT: %s', value in report_value)
            return value in report_value
        else:
            logging.error('Field is not a string or list: %s', report_value)
            return None

    try:
        if operator in ['>', '>=', '<', '<=']:
            report_value = int(report_value)
            value = int(value)
    except ValueError as e:
        logging.error('Value error: cannot cast value to integer: %s', e)
        return None

    # Evaluate the query
    if operator == '=':
        return report_value == value
    elif operator == '!=':
        return report_value != value
    elif operator == '>':
        return report_value > value
    elif operator == '>=':
        return report_value >= value
    elif operator == '<':
        return report_value < value
    elif operator == '<=':
        return report_value <= value
    elif operator == 'contains':
        pass
    else:
        logging.error('Invalid operator: %s', operator)
        return None
