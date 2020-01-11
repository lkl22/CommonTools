import unittest
from util.DateUtil import *


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual("2020-01-10 10:23:53", DateUtil.timestamp2Time(1578623033))
        self.assertEqual(1578623033, DateUtil.time2Timestamp("2020-01-10 10:23:53"))


if __name__ == '__main__':
    unittest.main()
