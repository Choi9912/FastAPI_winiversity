# Generate a SECRET_KEY using Python

import secrets


def generate_secret_key(length=32):
    return secrets.token_hex(length)


if __name__ == "__main__":
    print(generate_secret_key())
