import json

from PyInquirer import ValidationError
from PyInquirer import Validator


class NumberValidator(Validator):
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:  # pragma: no cover
            raise ValidationError(
                message='Please enter a number',
                cursor_position=len(document.text))  # pragma: no cover
        if int(document.text) < 0 or int(document.text) > 65535:
            raise ValidationError(
                message='Please enter a number between 0 and 65535',
                cursor_position=len(document.text))  # pragma: no cover


class MCCValidator(Validator):
    def validate(self, document):
        try:
            int(document.text.lstrip('0'))
        except ValueError:  # pragma: no cover
            raise ValidationError(
                message='Please enter a number',
                cursor_position=len(document.text))  # pragma: no cover
        if int(document.text.lstrip('0')) < 0 or int(document.text.lstrip('0')) > 999 or len(document.text) != 3:
            raise ValidationError(
                message='Please enter a number between 000 and 999',
                cursor_position=len(document.text))  # pragma: no cover


class MNCValidator(Validator):
    def validate(self, document):
        try:
            int(document.text.lstrip('0'))
        except ValueError:  # pragma: no cover
            raise ValidationError(
                message='Please enter a number',
                cursor_position=len(document.text))  # pragma: no cover
        if int(document.text.lstrip('0')) < 0 or int(document.text.lstrip('0')) > 99 or len(document.text) != 2:
            raise ValidationError(
                message='Please enter a number between 00 and 99',
                cursor_position=len(document.text))  # pragma: no cover


class IMSIValidator(Validator):
    def validate(self, document):
        imsi = None
        try:
            imsi = json.loads(document.text)
        except Exception as e:  # pragma: no cover
            raise ValidationError(
                message='Not valid JSON',
                cursor_position=len(document.text))  # pragma: no cover
        if not isinstance(imsi, list):
            raise ValidationError(
                message='Must be a list of IMSI records',
                cursor_position=len(document.text))  # pragma: no cover
