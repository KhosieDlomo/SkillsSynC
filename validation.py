def valid_input(password, email):
    if len(password) < 8:
        return False

    has_digit = False
    has_lowercase = False
    has_uppercase = False
    has_specialChar = False

    for char in password:
        if char.isdigit():
            has_digit = True
        if char.islower():
            has_lowercase = True
        if char.isupper():
            has_uppercase = True
        if not char.isalnum(): 
            has_specialChar = True

    if not has_digit:
        return False
    if not has_lowercase:
        return False
    if not has_uppercase:
        return False
    if not has_specialChar:
        return False
   
    if '@gmail.com' not in email:
        return False

    return email, password
    