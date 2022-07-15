# -*- coding: utf-8 -*-
"""
Test module for daedalus.
@author: Charlie Lewis
"""
from daedalus.daedalus import Daedalus


def test_start_remove_dovesnap():
    instance = Daedalus()
    # hack conf_dir since it's not installed as a library
    instance.set_config_dir(conf_dir='/blue/5G')
    instance.start_dovesnap()
    instance.remove_dovesnap()
    instance.reset_cwd()


def test_build_images():
    instance = Daedalus()
    # hack conf_dir since it's not installed as a library
    instance.set_config_dir(conf_dir='/Daedalus/blue/5G')
    instance.build_dockers(srsran=True, ueransim=True,
                           open5gs=True, srsran_lime=True)
    instance.reset_cwd()


def test_create_remove_networks():
    instance = Daedalus()
    # hack conf_dir since it's not installed as a library
    instance.set_config_dir(conf_dir='/..')
    instance.start_dovesnap()
    instance.create_networks()
    instance.remove_networks()
    instance.remove_dovesnap()
    instance.reset_cwd()


def test_start_no_services():
    instance = Daedalus()
    instance.start_services()


def test_remove_no_services():
    instance = Daedalus()
    instance.remove_services()


def test_start_remove_services():
    instance = Daedalus()
    # hack conf_dir since it's not installed as a library
    instance.set_config_dir(conf_dir='/..')
    instance.start_dovesnap()
    instance.create_networks()
    instance.compose_files = ['-f', 'core/epc.yml',
                              '-f', 'core/upn.yml', '-f', 'core/db.yml']
    instance.start_services()
    instance.remove_services()
    instance.cleanup()


def test_main_questions():
    instance = Daedalus()
    instance.main_questions()


def test_global_number_questions():
    instance = Daedalus()
    instance.global_number_questions('enb')


def test_sdr_questions():
    instance = Daedalus()
    instance.sdr_questions('enb')


def test_imsi_questions():
    instance = Daedalus()
    instance.imsi_questions()


def test_running_questions():
    instance = Daedalus()
    instance.running_questions()


def test_check_commands():
    instance = Daedalus()
    instance.check_commands()
