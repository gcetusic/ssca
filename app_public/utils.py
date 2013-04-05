"""
Utils module contains app_public specific 
utility/common/convenience/helper functions
"""
import string
import random


def generate_random_str(length=64, charset=string.ascii_uppercase + string.digits):
    """
    function generates a random for given length and charsetet
    """
    return ''.join(random.choice(charset) for x in range(length))


def get_rendon_alphanum64():
    """
    function generates a random 64 byte hash
    """
    return generate_random_str()


# internal test cases
if __name__ == "__main__":
    for i in range(1,21):
        print get_rendon_alphanum64()
