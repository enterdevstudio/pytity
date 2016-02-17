import pytest

from pytity import Manager


@pytest.fixture
def manager():
    return Manager()
