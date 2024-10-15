from django.core.exceptions import ValidationError
import re
from django.utils.translation import gettext_lazy as _


def ValidateEmailImpl(email):
    from .models import User, Artist
    from django.contrib.auth.models import User
    """ Validate that the email is unique. """
    if User.objects.filter(email=email).exists():
        raise ValidationError(f"A user with {email} already exists.")
    
    if Artist.objects.filter(email=email).exists():
        raise ValidationError(f"A user with {email} already exists in Artist Profile.")


def ValidateNameImpl(name):
    """ Validate that the name contains only letters (a-z, A-Z). """
    if not re.match(r'^[A-Za-z]+$', name):
        raise ValidationError("Must contain only letters (a-z, A-Z) and cannot contain spaces or special characters.")

def ValidateUserNameImpl(username):
    from .models import User, Artist
    from django.contrib.auth.models import User
    """ Validate UserName if present and length of username between 4 and 30 characters"""
    if User.objects.filter(username=username).exists():
        raise ValidationError(_("This username is already taken. Please choose another."))
    
    if not username or username.strip() == "":
        raise ValidationError("UserName Cannot be empty.")

    # Check the length of the username
    if len(username) < 4 or len(username) > 30:
        raise ValidationError(_("Username must be between 4 and 30 characters."))
    
    # Check if the username starts with a number
    if re.match(r'^\d', username):
        raise ValidationError(_("Username cannot start with a number."))
    
    # Check if the username contains any special characters
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', username):
        raise ValidationError(_("Username cannot contain special characters."))
    
def ValidatePhoneNumberImpl(number):
    """Validate that the phone number is 10 digits long and contains only numbers."""
    if not re.match(r'^\d{10}$', number):
        raise ValidationError('Phone number must be exactly 10 digits and contain only numbers.')


def ValidateStringImpl(value):
    """Validate address if it is null and it has special characters or not"""
    if not value or value.strip() == "":
        raise ValidationError("Cannot be empty.")
    
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError(f"{value} cannot contain special characters.")
    
    if re.search(r'\d', value):
        raise ValidationError(f"{value} cannot contain numbers.")
    
def ValidateAddressImpl(value):
    """Validate address if it is null and it has special characters or not"""
    if not value or value.strip() == "":
        raise ValidationError("Address cannot be empty.")
    
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError(f"{value} cannot contain special characters.")
    

def ValidatePriceImpl(price):
    """Validate Price if negative price is entered or if the price is set to threshold price"""
    if price < 0:
        raise ValidationError("Price cannot be negative")
    

def ValidateTitleImpl(value):
    if not re.match(r'^[A-Za-z\s]+$', value):
        raise ValidationError("Title must contain only letters and spaces, and cannot contain numbers or special characters.")
    