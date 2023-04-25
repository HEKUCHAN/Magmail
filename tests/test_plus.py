import pytest

def sum_2_value(a, b):
    return a + b

def test_plus():
    ret = sum_2_value(1, 2)
    assert ret == 3
