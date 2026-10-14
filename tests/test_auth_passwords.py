import unittest

from config import bcrypt_context


class PasswordHashTests(unittest.TestCase):
    def test_password_hash_can_be_verified(self):
        password = "SenhaTeste123!"
        password_hash = bcrypt_context.hash(password)

        self.assertTrue(bcrypt_context.verify(password, password_hash))
        self.assertFalse(bcrypt_context.verify("senha-incorreta", password_hash))


if __name__ == "__main__":
    unittest.main()