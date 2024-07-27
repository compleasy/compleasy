from pyparsing import Word, alphas, nums, oneOf, quotedString, ParseException, Suppress, Optional, Combine
import logging
from django.db.models import Q
from django.apps import apps
from utils.lynis_report import LynisReport

# Define the components of the query
word = Word(alphas + '_')
operator = oneOf("= != > < >= <=")
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
    """Evaluate a query against a report, so we can determine if a device is compliant with a policy."""
    """Query example: hardening_index > 80"""
    parsed_query = parse_query(query)
    if not parsed_query or len(parsed_query) < 3:
        logging.error('Invalid query: %s', query)
        return None
    logging.debug('Parsed query: %s', parsed_query)

    # Get the field name and the operator
    field, operator, value = parsed_query
    logging.debug('Field: %s, operator: %s, value: %s', field, operator, value)

    # Get full report from report object and parse it using LynisReport class
    report_value = report.get(field)
    logging.debug('Report value: %s', report_value)

    if not report_value:
        logging.error('Field not found in report: %s', field)
        return None
    
    try:
        if operator in ['>', '>=', '<', '<=']:
            report_value = int(report_value)
            value = int(value)
    except ValueError as e:
        logging.error('Value error: cannot cast value to integer: %s', e)

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
    else:
        logging.error('Invalid operator: %s', operator)
        return None