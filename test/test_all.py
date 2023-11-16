# SUPER SECRET CONFIDENTIAL 
# [2023] - [Infinity and Beyond] ACME CO 
# All Rights Reserved. 
# NOTICE: This is super secret info that 
# must be protected at all costs. 

import pytest

from app.main import HeaderPy
from app.headerrc import HeaderRC
import mock


class TestAll:
    @classmethod
    def setup_class(cls):
        """
        Runs 1 time before all tests in this class
        """
        
    @mock.patch.object(HeaderRC, '_load_default_yml')
    @mock.patch.object(HeaderRC, '_load_user_yml')
    def test_negagate_characters(self, _load_default_yml, _load_user_yml):
        mock_yml = {
            'negagate_characters': "++",
        }
        _load_default_yml.return_value = mock_yml
        _load_user_yml.return_value = mock_yml

        h = HeaderRC()
        assert h.negate_characters == "++"
        
        mock_yml["negagate_characters"] = "!"
        _load_user_yml.return_value = mock_yml
        h = HeaderRC()
        assert h.negate_characters == "!"
        
        del mock_yml["negagate_characters"]
        _load_user_yml.return_value = mock_yml
        h = HeaderRC()
        assert h.negate_characters == "!"
        