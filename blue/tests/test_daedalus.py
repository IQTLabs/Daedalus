# -*- coding: utf-8 -*-
"""
Test module for daedalus.
@author: Charlie Lewis
"""
import time
from daedalus.daedalus import Daedalus


def test_start_remove_dovesnap():
    instance = Daedalus()
    instance.start_dovesnap()
    instance.remove_dovesnap()
    instance.reset_cwd()
    instance.cleanup()


def test_build_images():
    instance = Daedalus()
    instance.build_dockers(srsran=True, ueransim=True,
                           open5gs=True)
    instance.reset_cwd()
    instance.cleanup()


def test_create_remove_networks():
    instance = Daedalus()
    instance.start_dovesnap()
    instance.create_networks()
    # TODO: workaround for dovesnap not handling creating then immediately deleting networks.
    time.sleep(5)
    instance.remove_networks()
    instance.remove_dovesnap()
    instance.reset_cwd()
    instance.cleanup()


def test_start_no_services():
    instance = Daedalus()
    instance.start_services()
    instance.cleanup()


def test_remove_no_services():
    instance = Daedalus()
    instance.remove_services()
    instance.cleanup()


def test_start_remove_services():
    instance = Daedalus()
    instance.start_dovesnap()
    instance.create_networks()
    instance.compose_files = [
        '-f', 'blue/5G/daedalus/5G/core/epc.yml',
        '-f', 'blue/5G/daedalus/5G/core/upn.yml',
        '-f', 'blue/5G/daedalus/5G/core/db.yml']
    instance.start_services()
    instance.remove_services()
    instance.cleanup()


def test_main_questions():
    instance = Daedalus()
    instance.main_questions()
    instance.cleanup()


def test_global_number_questions():
    instance = Daedalus()
    instance.global_number_questions('enb')
    instance.cleanup()


def test_sdr_questions():
    instance = Daedalus()
    instance.sdr_questions('enb')
    instance.cleanup()


def test_imsi_questions():
    instance = Daedalus()
    instance.imsi_questions()
    instance.cleanup()


def test_running_questions():
    instance = Daedalus()
    instance.running_questions()
    instance.cleanup()


def test_check_commands():
    instance = Daedalus()
    instance.check_commands()
    instance.cleanup()
