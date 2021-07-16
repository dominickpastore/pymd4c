import pytest

def pytest_addoption(parser):
    parser.addoption("--md4c-version", action="store", help="Specify which "
                     "version of MD4C is in use for these tests")
