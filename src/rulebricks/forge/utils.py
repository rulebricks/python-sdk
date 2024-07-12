import string
import random

def generate_slug(length=10):
    """
    Generate a random alphanumeric slug.

    Args:
        length (int): The length of the slug to generate. Defaults to 10.

    Returns:
        str: A random alphanumeric slug.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
