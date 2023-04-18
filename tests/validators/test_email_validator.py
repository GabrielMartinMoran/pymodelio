import pytest

from pymodelio.exceptions.model_validation_exception import ModelValidationException
from pymodelio.validators import EmailValidator


def test_validate_does_not_raise_error_when_provided_value_is_none_and_property_is_nullable():
    validator = EmailValidator(nullable=True)
    validator.validate(None, '')


def test_validate_raises_validation_error_when_provided_value_is_none_and_property_is_not_nullable():
    validator = EmailValidator(nullable=False)
    with pytest.raises(ModelValidationException) as ex_info:
        validator.validate(None, 'prop')
    assert ex_info.value.args[0] == 'prop must not be None'


def test_validate_raises_validation_error_when_provided_value_is_not_a_valid_email_address():
    validator = EmailValidator()
    # List obtained from: https://gist.github.com/cjaoude/fd9910626629b53c4d25
    invalid_email_addresses = [
        'plainaddress',
        '#@%^%#$@#$@#.com',
        '@example.com',
        'Joe Smith <email@example.com>',
        'email.example.com',
        'email@example@example.com',
        '.email@example.com',
        'email.@example.com',
        'email..email@example.com',
        'あいうえお@example.com',
        'email@example.com (Joe Smith)',
        'email@example',
        'email@-example.com',
        'email@example..com',
        'Abc..123@example.com',
        '”(),:;<>[\\]@example.com',
        'just”not”right@example.com',
        'this\\ is"really"not\\allowed@example.com'
    ]
    for invalid_email_address in invalid_email_addresses:
        with pytest.raises(ModelValidationException) as ex_info:
            validator.validate(invalid_email_address, invalid_email_address)
        assert ex_info.value.args[0] == f'{invalid_email_address} is not instance of email address'


def test_validate_does_not_raise_error_when_property_is_a_valid_email_address():
    validator = EmailValidator()
    # List obtained from: https://gist.github.com/cjaoude/fd9910626629b53c4d25
    valid_email_addresses = [
        'email@example.com',
        'firstname.lastname@example.com',
        'email@subdomain.example.com',
        'firstname+lastname@example.com',
        'email@123.123.123.123',
        '1234567890@example.com',
        'email@example-one.com',
        '_______@example.com',
        'email@example.name',
        'email@example.museum',
        'email@example.co.jp',
        'firstname-lastname@example.com'
    ]
    valid_email_addresses += [x.upper() for x in valid_email_addresses]
    for valid_email_address in valid_email_addresses:
        validator.validate(valid_email_address, valid_email_address)
