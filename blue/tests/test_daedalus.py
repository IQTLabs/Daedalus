# -*- coding: utf-8 -*-
"""
Test module for daedalus.
@author: Charlie Lewis
"""
from daedalus.daedalus import Daedalus


def test_start_remove_dovesnap():
    instance = Daedalus()
    instance.start_dovesnap()
    instance.remove_dovesnap()
