import pytest
import mock
from mock import MagicMock, mock_open

from app.headerrc import HeaderRC, File_Mode
from app.main import HeaderPy

class TestHeaderRCSettings:
    @classmethod
    def setup_class(cls):
        """
        Runs 1 time before all tests in this class
        """
        pass
    
    def test_test(self):
        assert True