import unittest
from app.lib.models import User


class UserTest(unittest.TestCase):
    def test_create(self):
        sub = 'uinttest'  # uinttest/lilijie
        res = User().create(sub)
        if not res:
            print('create user ' + sub + ' error')
            self.assertEqual(res, True)
            return
        print('create user ' + sub + ' success')
        self.assertEqual(res, res)

    def test_login(self):
        sub = 'lilijie'
        pwd = '123456'  # 123456/12345
        res = User().load({'sub': sub, 'pwd': pwd}).login()
        if not res:
            print('login user ' + sub + ' error')
            self.assertEqual(res, True)
            return
        print('login user ' + sub + ' success')
        self.assertEqual(res, res)

    def test_del(self):
        sub = 'unit'  # uinttest/unit
        res = User().load({'sub': sub}).delete()
        if not res:
            print('delete user ' + sub + ' error')
            self.assertEqual(res, True)
            return
        print('delete user ' + sub + ' success')
        self.assertEqual(res, res)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(UserTest('test_create'))
    suite.addTest(UserTest('test_login'))
    suite.addTest(UserTest('test_del'))

    runner = unittest.TextTestRunner()
    runner.run(suite)
