"""
Module for validating user input
"""
import json

from inquirer.errors import ValidationError

def validate_number (answers, current):
    """Specifically validate the string is a number between 0 and 66535"""
    try:
        int(current)
    except ValueError as value_error:  # pragma: no cover
        raise ValidationError( "", 
            reason='Please enter a number') from value_error  # pragma: no cover
    if int(current) < 0 or int(current) > 65535:
        raise ValidationError( "",
            reason='Please enter a number between 0 and 65535')  # pragma: no cover

def validate_mcc(answers, current):
    """Specifically validate the string is a number between 000 and 999"""
    try:
        int(current.lstrip('0'))
    except ValueError as value_error:  # pragma: no cover
        raise ValidationError("",
            reason='Please enter a number') from value_error  # pragma: no cover
    if int(current.lstrip('0')) < 0 or int(current.lstrip('0')) > 999 or len(current) != 3:
        raise ValidationError("",
            reason='Please enter a number between 000 and 999')  # pragma: no cover

def validate_mnc(answers, current):
    """Specifically validate the string is a number between 00 and 99"""
    try:
        int(current.lstrip('0'))
    except ValueError as value_error:  # pragma: no cover
        raise ValidationError("",
            reason='Please enter a number') from value_error  # pragma: no cover
    if int(current.lstrip('0')) < 0 or int(current.lstrip('0')) > 99 or len(current) != 2:
        raise ValidationError("",
            reason='Please enter a number between 00 and 99')  # pragma: no cover

def validate_imsi(answers, current):
    """Specifically validate the string is a JSON parsable list of records"""
    imsi = None
    try:
        imsi = json.loads(current)
    except Exception as err:  # pragma: no cover
        raise ValidationError("",
            reason='Not valid JSON') from err  # pragma: no cover
    if not isinstance(imsi, list):
        raise ValidationError("",
            reason='Must be a list of IMSI records')  # pragma: no cover
