def email_validation(email):
    if "@" in email and "." in email:
        return True
    return False