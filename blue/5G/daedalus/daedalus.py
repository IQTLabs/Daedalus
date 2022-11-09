"""
Daedalus module for creating and running 4G/5G environments with any
combination of simulation and real SDRs
"""
import argparse
import json
import logging
import os
import sys
import time

import docker as dclient
from daedalus import __file__
from daedalus import __version__
from daedalus.validators import validate_imsi
from daedalus.validators import validate_mcc
from daedalus.validators import validate_mnc
from daedalus.validators import validate_number
from daedalus.styles import custom_style
from plumbum import FG  # pytype: disable=import-error
from plumbum import local  # pytype: disable=import-error
from plumbum import TF  # pytype: disable=import-error
from plumbum.cmd import chown  # pytype: disable=import-error
from plumbum.cmd import cp  # pytype: disable=import-error
from plumbum.cmd import curl  # pytype: disable=import-error
from plumbum.cmd import docker  # pytype: disable=import-error
from plumbum.cmd import docker_compose  # pytype: disable=import-error
from plumbum.cmd import ip  # pytype: disable=import-error
from plumbum.cmd import ls  # pytype: disable=import-error
from plumbum.cmd import mkdir  # pytype: disable=import-error
from plumbum.cmd import rm  # pytype: disable=import-error
from plumbum.cmd import sudo  # pytype: disable=import-error
from plumbum.cmd import tar  # pytype: disable=import-error
from inquirer import prompt, Checkbox, Confirm, Editor, List, Text


level_int = {'CRITICAL': 50, 'ERROR': 40, 'WARNING': 30, 'INFO': 20,
             'DEBUG': 10}
level = level_int.get(os.getenv('LOGLEVEL', 'INFO').upper(), 0)
logging.basicConfig(level=level)


class Daedalus():
    """
    Main Daedalus class for creating and running 4G/5G environments with any
    combination of simulation and real SDRs
    """

    def __init__(self, raw_args=None):
        # defaults
        self.bladerf_prb = '50'
        self.ettus_prb = '50'
        self.limesdr_prb = '50'
        self.bladerf_earfcn = '3400'
        self.ettus_earfcn = '1800'
        self.limesdr_earfcn = '900'
        self.bladerf_txgain = '80'
        self.bladerf_rxgain = '40'
        self.ettus_txgain = '80'
        self.ettus_rxgain = '40'
        self.limesdr_txgain = '80'
        self.limesdr_rxgain = '40'
        self.mcc = '001'
        self.mnc = '01'

        self.raw_args = raw_args
        self.compose_files = []
        self.options = []
        self.previous_dir = os.getcwd()

    @staticmethod
    def build_dockers(srsran=False, ueransim=False, open5gs=False, srsran_lime=False):
        """Build Docker images for the various components"""
        version = 'latest'
        if not 'dev' in __version__:
            version = 'v'+__version__

        if srsran:
            srsran_version = 'release_22_04_1'
            srs_args = ['build', '-t', 'iqtlabs/srsran:'+version, '-f', 'Dockerfile',
                        '--build-arg', f'SRS_VERSION={srsran_version}', '.']
            with local.cwd(local.cwd / 'blue/5G/daedalus/5G/srsRAN'):
                docker.bound_command(srs_args) & FG
        if srsran_lime:
            srsran_version = 'release_19_12'
            srs_args = ['build', '-t', 'iqtlabs/srsran-lime:'+version, '-f', 'Dockerfile',
                        '--build-arg', f'SRS_VERSION={srsran_version}', '.']
            with local.cwd(local.cwd / 'blue/5G/daedalus/5G/srsRAN'):
                docker.bound_command(srs_args) & FG
        if ueransim:
            args = ['build', '-t', 'iqtlabs/ueransim:'+version, '.']
            with local.cwd(local.cwd / 'blue/5G/daedalus/5G/UERANSIM'):
                docker.bound_command(args) & FG
        if open5gs:
            args = ['build', '-t', 'iqtlabs/open5gs:'+version, '.']
            with local.cwd(local.cwd / 'blue/5G/daedalus/5G/open5gs'):
                docker.bound_command(args) & FG

    def start_dovesnap(self):
        """Start Dovesnap components in Docker containers"""
        release = 'v1.1.4'
        faucet_prefix = '/tmp/tpfaucet'
        sudo[ip['link', 'add', 'tpmirrorint', 'type', 'veth',
                'peer', 'name', 'tpmirror']](retcode=(0, 2))
        sudo[ip['link', 'set', 'tpmirrorint', 'up']]()
        sudo[ip['link', 'set', 'tpmirror', 'up']]()
        sudo[rm['-rf', f'{faucet_prefix}']]()
        sudo[rm['-rf', local.cwd // 'IQTLabs-dovesnap-*']]()
        mkdir['-p', f'{faucet_prefix}/etc/faucet']()
        cp[f'{os.path.dirname(__file__)}/5G/configs/faucet/faucet.yaml', f'{faucet_prefix}/etc/faucet/']()
        cp[f'{os.path.dirname(__file__)}/5G/configs/faucet/acls.yaml', f'{faucet_prefix}/etc/faucet/']()
        curl['-LJO',
             f'https://github.com/iqtlabs/dovesnap/tarball/{release}']()
        tar['-xvf', local.cwd // 'IQTLabs-dovesnap-*.tar.gz']()
        rm[local.cwd // 'IQTLabs-dovesnap-*.tar.gz']()
        args = ['-f', 'docker-compose.yml', '-f',
                'docker-compose-standalone.yml', 'up', '-d', '--build']
        dovesnap_dir = local.cwd // 'IQTLabs-dovesnap-*'
        with local.env(MIRROR_BRIDGE_OUT='tpmirrorint',
                       FAUCET_PREFIX=f'{faucet_prefix}'):
            with local.cwd(dovesnap_dir[0]):
                try:
                    docker_compose.bound_command(args) & FG
                except Exception as err:  # pragma: no cover
                    logging.error(
                        'Failed to start dovesnap because: %s\nCleaning up and quitting.', err)
                    self.cleanup()

    @staticmethod
    def create_networks():
        """Create necessary Dovesnap networks as Docker networks"""
        dovesnap_opts = ['network', 'create', '-o',
                         'ovs.bridge.controller=tcp:127.0.0.1:6653,tcp:127.0.0.1:6654',
                         '-o', 'ovs.bridge.mtu=9000', '-o', 'ovs.bridge.preallocate_ports=15',
                         '--ipam-opt', 'com.docker.network.driver.mtu=9000', '--internal',
                         '-d', 'dovesnap']
        cpn_opts = ['-o', 'ovs.bridge.vlan=26', '-o', 'ovs.bridge.dpid=0x620',
                    '-o', 'ovs.bridge.mode=routed', '--subnet', '192.168.26.0/24',
                    '--gateway', '192.168.26.1', '--ipam-opt',
                    'com.docker.network.bridge.name=cpn', '-o',
                    'ovs.bridge.nat_acl=protectcpn', 'cpn']
        upn_opts = ['-o', 'ovs.bridge.vlan=27', '-o', 'ovs.bridge.dpid=0x630',
                    '-o', 'ovs.bridge.mode=nat', '--subnet', '192.168.27.0/24',
                    '--gateway', '192.168.27.1', '--ipam-opt',
                    'com.docker.network.bridge.name=upn', 'upn']
        rfn_opts = ['-o', 'ovs.bridge.vlan=28', '-o', 'ovs.bridge.dpid=0x640',
                    '-o', 'ovs.bridge.mode=flat', '--subnet', '192.168.28.0/24',
                    '--ipam-opt', 'com.docker.network.bridge.name=rfn', '-o',
                    'ovs.bridge.nat_acl=protectrfn', 'rfn']
        ran_opts = ['-o', 'ovs.bridge.vlan=29', '-o', 'ovs.bridge.dpid=0x650',
                    '-o', 'ovs.bridge.mode=routed', '--subnet', '192.168.29.0/24',
                    '--gateway', '192.168.29.1', '--ipam-opt',
                    'com.docker.network.bridge.name=ran', '-o',
                    'ovs.bridge.nat_acl=protectran', 'ran']
        docker.bound_command(dovesnap_opts + cpn_opts) & FG
        docker.bound_command(dovesnap_opts + upn_opts) & FG
        docker.bound_command(dovesnap_opts + rfn_opts) & FG
        docker.bound_command(dovesnap_opts + ran_opts) & FG

    def start_services(self):
        """Start selected services for the 4G/5G environment"""
        if len(self.compose_files) > 0:
            compose_up = self.compose_files + ['up', '-d', '--build']
            smf = ''
            if 'core' in self.options:
                smf = '5GC'
            # TODO handle multiple SDRs of the same type
            with local.env(BLADERF_PRB=self.bladerf_prb,
                           BLADERF_EARFCN=self.bladerf_earfcn,
                           ETTUS_PRB=self.ettus_prb,
                           ETTUS_EARFCN=self.ettus_earfcn,
                           LIMESDR_PRB=self.limesdr_prb,
                           LIMESDR_EARFCN=self.limesdr_earfcn,
                           BLADERF_TXGAIN=self.bladerf_txgain,
                           BLADERF_RXGAIN=self.bladerf_rxgain,
                           ETTUS_TXGAIN=self.ettus_txgain,
                           ETTUS_RXGAIN=self.ettus_rxgain,
                           LIMESDR_TXGAIN=self.limesdr_txgain,
                           LIMESDR_RXGAIN=self.limesdr_rxgain, SMF=smf):
                try:
                    docker_compose.bound_command(compose_up) & FG
                except Exception as err:  # pragma: no cover
                    logging.error(
                        'Failed to start services because: %s\nCleaning up and quitting.', err)
                    self.cleanup()
        else:
            logging.warning('No services to start, quitting.')

    def follow_logs(self):
        """Follow logs from selected services using Docker"""
        if len(self.compose_files) > 0:
            compose_logs = self.compose_files + ['logs', '-f']
            try:
                docker_compose.bound_command(compose_logs) & TF(None, FG=True)
            except Exception as err:  # pragma: no cover
                logging.error(
                    'Failed to follow logs because: %s\nReturning to menu in 3 seconds.', err)
                time.sleep(3)
        else:
            logging.warning('No services to log.')

    @staticmethod
    def remove_dovesnap():
        """Remove the Dovesnap containers"""
        args = ['-f', 'docker-compose.yml', '-f', 'docker-compose-standalone.yml',
                'down', '--volumes', '--remove-orphans']
        dovesnap_dir = local.cwd // 'IQTLabs-dovesnap-*'
        if len(dovesnap_dir) == 0:
            return
        with local.cwd(dovesnap_dir[0]):
            logging.debug('Removing Dovesnap services')
            try:
                docker_compose.bound_command(args) & FG
            except Exception as err:  # pragma: no cover
                logging.debug('%s', err)
        # ensure the dovesnap network has been removed
        try:
            dovesnap_path = local['echo'][dovesnap_dir]()
            dovesnap_network = dovesnap_path.split('/')[-1].strip().lower()
            dn_args = ['network', 'rm', dovesnap_network+'_dovesnap']
            docker.bound_command(dn_args) & FG
        except Exception as err:  # pragma: no cover
            logging.debug('%s', err)

    @staticmethod
    def remove_networks():
        """Remove the Dovesnap Docker networks"""
        cpn_args = ['network', 'rm', 'cpn']
        upn_args = ['network', 'rm', 'upn']
        rfn_args = ['network', 'rm', 'rfn']
        ran_args = ['network', 'rm', 'ran']
        try:
            logging.info('Removing cpn network')
            docker.bound_command(cpn_args) & FG
        except Exception as err:  # pragma: no cover
            logging.debug('%s', err)
        try:
            logging.info('Removing upn network')
            docker.bound_command(upn_args) & FG
        except Exception as err:  # pragma: no cover
            logging.debug('%s', err)
        try:
            logging.info('Removing rfn network')
            docker.bound_command(rfn_args) & FG
        except Exception as err:  # pragma: no cover
            logging.debug('%s', err)
        try:
            logging.info('Removing ran network')
            docker.bound_command(ran_args) & FG
        except Exception as err:  # pragma: no cover
            logging.debug('%s', err)

    def remove_services(self):
        """Remove the services started as Docker containers"""
        if len(self.compose_files) > 0:
            logging.debug('Removing Daedalus services')
            compose_down = self.compose_files + \
                ['down', '--volumes', '--remove-orphans']
            try:
                docker_compose.bound_command(compose_down) & FG
            except Exception as err:  # pragma: no cover
                logging.debug('%s', err)
        else:
            logging.warning('No services to remove.')

    @staticmethod
    def execute_prompt(questions):
        """
        Run end user prompt with supplied questions and return the selected
        answers
        """
        answers = prompt(questions, theme=custom_style())
        return answers

    @staticmethod
    def main_questions():
        """Ask which services to start"""
        return [
            Checkbox('services',
                message = 'What services would you like to start?',
                choices = [
                    '4G Open5GS EPC (HSS, MME, SMF, SGWC, PCRF)',
                    'Open5GS User Plane Network (UPF, SGWU)',
                    'Subscriber Database (MongoDB)',
                    '5G Open5GS Core (NRF, AUSF, NSSF, UDM, BSF, PCF, UDR, AMF)',
                    '5G UERANSIM gNodeB (gNB)',
                    '4G srsRAN eNodeB (eNB)',
                    '5G srsRAN NSA gNodeB (gNB)',
                    '4G BladeRF eNodeB (eNB)',
                    '4G Ettus USRP B2xx eNodeB (eNB)',
                    '5G Ettus USRP B2xx NSA gNodeB (gNB)',
                    '4G LimeSDR eNodeB (eNB)',
                    '4G srsRAN UE (UE)',
                    '5G srsRAN UE (UE)',
                    '5G UERANSIM UE (UE)',
                    'Add UE IMSIs',
                    'Subscriber WebUI',
                ],
                default = [
                    '4G Open5GS EPC (HSS, MME, SMF, SGWC, PCRF)',
                    'Open5GS User Plane Network (UPF, SGWU)',
                    'Subscriber Database (MongoDB)'
                ]
            ),
        ]

    @staticmethod
    def global_number_questions(enb):
        """Ask which codes to use"""
        return [
            Text(
                'mcc',
                message = f'What MCC code for {enb} would you like?',
                default = '001',
                validate = validate_mcc,
            ),
            Text(
                'mnc',
                message = f'What MNC code for {enb} would you like?',
                default = '01',
                validate = validate_mnc,
            ),
        ]

    @staticmethod
    def sdr_questions(enb):
        """Ask SDR specific questions"""
        return [
            List(
                'prb',
                message = f'Number of Physical Resource Blocks (PRB) for {enb}',
                choices = ['6', '15', '25', '50', '75', '100'],
                default = '50',
            ),
            Text(
                'earfcn',
                message = f'What EARFCN code for DL for {enb} would you like?',
                default = '3400',
                # TODO should also validate the EARFCN wasn't already used
                validate = validate_number,
            ),
            Text(
                'txgain',
                message = f'What TX gain value for {enb} would you like?',
                default = '80',
                validate = validate_number,
            ),
            Text(
                'rxgain',
                message = f'What RX gain value for {enb} would you like?',
                default = '40',
                validate = validate_number,
            ),
        ]

    @staticmethod
    def imsi_questions():
        """Ask IMSI specific questions"""
        example_imsi = '''[{{
    "access_restriction_data": 32,
    "ambr": {{
      "downlink": {{
        "unit": 3,
        "value": 1
      }},
      "uplink": {{
        "unit": 3,
        "value": 1
      }}
    }},
    "imsi": "001010000000012",
    "network_access_mode": 2,
    "security": {{
      "amf": "8000",
      "k": "c8eba87c1074edd06885cb0486718341",
      "op": null,
      "opc": "17b6c0157895bcaa1efc1cef55033f5f"
    }},
    "slice": [
      {{
        "default_indicator": true,
        "sd": "000000",
        "session": [
          {{
            "ambr": {{
              "downlink": {{
                "unit": 3,
                "value": 1
              }},
              "uplink": {{
                "unit": 3,
                "value": 1
              }}
            }},
            "name": "internet",
            "pcc_rule": [],
            "qos": {{
              "arp": {{
                "pre_emption_capability": 1,
                "pre_emption_vulnerability": 1,
                "priority_level": 8
              }},
              "index": 9
            }},
            "type": 1
          }}
        ],
        "sst": 1
      }}
    ],
    "subscribed_rau_tau_timer": 12,
    "subscriber_status": 0
  }}]'''

        return [
            Editor(
                'imsi',
                message = 'Add a new IMSI (an example will be prepopulated to get you started)',
                default = example_imsi,
                #default = f'{json.dumps(json.dumps(example_imsi, indent=2))}',
                # 'eargs': {
                #     'editor': 'nano',
                #     'ext': '.json',
                # },
                validate = validate_imsi,
            ),
            Confirm(
                'add_imsi',
                message = 'Would you like to add another IMSI?',
                default = False,
            ),
        ]

    @staticmethod
    def running_questions():
        """Once services are running, ask questions of what to do next"""
        return [
            List(
                'actions',
                message = 'Services have started, what would you like to do?',
                choices = [
                    'Follow logs (Ctrl-c to return to this menu)',
                    'Remove services',
                    'Quit (services that were not removed will continue to run)',
                ],
            ),
        ]

    def cleanup(self):
        """Cleanup any Daedalus environments that might still be around"""
        logging.info(
            'Cleaning up any previously running Daedalus environments...')
        client = dclient.from_env()
        containers = client.containers.list(
            filters={'label': 'daedalus.namespace=primary'})

        for container in containers:
            try:
                logging.debug('Removing container: %s', container.name)
                container.remove(force=True)
            except Exception as err:  # pragma: no cover
                logging.debug('%s', err)
        self.remove_networks()
        self.remove_dovesnap()

    @staticmethod
    def check_commands():
        """
        Check that the necessary commands for Daedalus exist on the system it's
        runnig on
        """
        logging.info(
            'Checking necessary commands exist, if it fails, install the missing tools.')
        chown['--version']()
        cp['--version']()
        curl['--version']()
        docker['--version']()
        docker_compose['--version']()
        ip['-V']()
        ls['--version']()
        mkdir['--version']()
        rm['--version']()
        sudo['--version']()
        tar['--version']()

    def loop(self):
        """Stay in a loop of options for the user until quitting is chosen"""
        running = True
        while running:
            answers = self.execute_prompt(self.running_questions())
            if 'actions' in answers:
                selections = answers['actions']
                if 'Follow logs (Ctrl-c to return to this menu)' in selections:
                    try:
                        self.follow_logs()
                    except KeyboardInterrupt:
                        pass
                if 'Remove services' in selections:
                    self.remove_services()
                    self.remove_networks()
                    self.remove_dovesnap()
                if 'Quit (services that were not removed will continue to run)' in selections:
                    running = False

    @staticmethod
    def _check_conf_dir(conf_dir):
        realpath = os.path.realpath(conf_dir)
        if not realpath.endswith('/5G'):
            raise ValueError(
                'last element of conf_dir must be 5G: %s' % realpath)
        for valid_prefix in ('/usr/local', '/opt', '/home'):
            if realpath.startswith(valid_prefix):
                return realpath
        raise ValueError('conf_dir root may not be safe: %s' % realpath)

    def set_config_dir(self, conf_dir='/5G'):
        """Set the current working directory to where the configs are"""
        try:
            realpath = self._check_conf_dir(
                os.path.dirname(__file__) + conf_dir)
            os.chdir(realpath)
            sudo[chown['-R', str(os.getuid()), '.']]()
        except Exception as err:  # pragma: no cover
            logging.error(
                'Unable to find config files, exiting because: %s', err)
            sys.exit(1)

    def reset_cwd(self):
        """Set the current working directory back to what it was originally"""
        os.chdir(self.previous_dir)

    def find_uhd(self):
        from plumbum.cmd import uhd_find_devices
        try:
            uhd_find_devices()
        except Exception as err:  # pragma: no cover
            logging.debug('%s', err)
            logging.error(
                'No UHD device found, but you chose Ettus. It is unlikely to work.')

    def parse_answers(self, answers):
        """
        Parses responses to which services to start to decide what happens next
        """
        build_srsran = False
        srsran_lime = False
        build_open5gs = False
        build_ueransim = False
        if 'services' in answers:
            selections = answers['services']
            if '4G Open5GS EPC (HSS, MME, SMF, SGWC, PCRF)' in selections:
                self.compose_files += ['-f', 'core/epc.yml']
                self.options.append('epc')
                build_open5gs = True
            else:
                logging.warning(
                    'No EPC was selected, this configuration is unlikely to work.')
            if 'Open5GS User Plane Network (UPF, SGWU)' in selections:
                self.compose_files += ['-f', 'core/upn.yml']
                self.options.append('upn')
                build_open5gs = True
            if 'Subscriber Database (MongoDB)' in selections:
                self.compose_files += ['-f', 'core/db.yml']
                self.options.append('db')
            else:
                logging.warning(
                    'No database was selected, this configuration is unlikely to work.')
            if '5G Open5GS Core (NRF, AUSF, NSSF, UDM, BSF, PCF, UDR, AMF)' in selections:
                self.compose_files += ['-f', 'core/core.yml']
                self.options.append('core')
                build_open5gs = True
            if '5G UERANSIM gNodeB (gNB)' in selections:
                self.compose_files += ['-f', 'SIMULATED/ueransim-gnb.yml']
                self.options.append('ueransim-gnb')
                build_ueransim = True
            if '4G srsRAN eNodeB (eNB)' in selections:
                self.compose_files += ['-f', 'SIMULATED/srsran-enb.yml']
                self.options.append('srsran-enb')
                build_srsran = True
            if '5G srsRAN NSA gNodeB (gNB)' in selections:
                self.compose_files += ['-f', 'SIMULATED/srsran-gnb.yml']
                self.options.append('srsran-gnb-nsa')
                build_srsran = True
            if '4G BladeRF eNodeB (eNB)' in selections:
                self.compose_files += ['-f', 'SDR/bladerf.yml']
                self.options.append('bladerf-enb')
                build_srsran = True
            if '4G Ettus USRP B2xx eNodeB (eNB)' in selections:
                self.compose_files += ['-f', 'SDR/ettus.yml']
                self.options.append('ettus-enb')
                self.find_uhd()
                build_srsran = True
            if '5G Ettus USRP B2xx NSA gNodeB (gNB)' in selections:
                self.compose_files += ['-f', 'SDR/ettus-gnb.yml']
                self.options.append('ettus-gnb')
                self.find_uhd()
                build_srsran = True
            if '4G LimeSDR eNodeB (eNB)' in selections:
                self.compose_files += ['-f', 'SDR/limesdr.yml']
                self.options.append('limesdr-enb')
                srsran_lime = True
            if '4G srsRAN UE (UE)' in selections:
                self.compose_files += ['-f', 'SIMULATED/srsran-ue.yml']
                self.options.append('srsran-ue')
                build_srsran = True
            if '5G srsRAN UE (UE)' in selections:
                self.compose_files += ['-f', 'SIMULATED/srsran-gue.yml']
                self.options.append('srsran-ue-nsa')
                build_srsran = True
            if '5G UERANSIM UE (UE)' in selections:
                self.compose_files += ['-f', 'SIMULATED/ueransim-ue.yml']
                self.options.append('ueransim-ue')
                build_ueransim = True
            if 'Add UE IMSIs' in selections:
                self.options.append('imsis')
            if 'Subscriber WebUI' in selections:
                self.compose_files += ['-f', 'core/ui.yml']
                self.options.append('webui')
                build_open5gs = True
        return build_srsran, srsran_lime, build_open5gs, build_ueransim

    def parse_sdrs(self):
        """Asks for SDR parameters and sets them"""
        sdrs = ['limesdr-enb', 'ettus-enb', 'bladerf-enb']
        for sdr in sdrs:
            if sdr in self.options:
                answers = self.execute_prompt(self.sdr_questions(sdr))
                if 'prb' in answers:
                    if sdr == 'bladerf-enb':
                        self.bladerf_prb = str(answers['prb'])
                    if sdr == 'ettus-enb':
                        self.ettus_prb = str(answers['prb'])
                    if sdr == 'limesdr-enb':
                        self.limesdr_prb = str(answers['prb'])
                if 'earfcn' in answers:
                    if sdr == 'bladerf-enb':
                        self.bladerf_earfcn = str(answers['earfcn'])
                    if sdr == 'ettus-enb':
                        self.ettus_earfcn = str(answers['earfcn'])
                    if sdr == 'limesdr-enb':
                        self.limesdr_earfcn = str(answers['earfcn'])
                if 'txgain' in answers:
                    if sdr == 'bladerf-enb':
                        self.bladerf_txgain = str(answers['txgain'])
                    if sdr == 'ettus-enb':
                        self.ettus_txgain = str(answers['txgain'])
                    if sdr == 'limesdr-enb':
                        self.limesdr_txgain = str(answers['txgain'])
                if 'rxgain' in answers:
                    if sdr == 'bladerf-enb':
                        self.bladerf_rxgain = str(answers['rxgain'])
                    if sdr == 'ettus-enb':
                        self.ettus_rxgain = str(answers['rxgain'])
                    if sdr == 'limesdr-enb':
                        self.limesdr_rxgain = str(answers['rxgain'])

    def write_imsis(self):
        """Asks for IMSI changes and writes them out to JSON"""
        if 'imsis' in self.options:
            adding_imsis = True
            while adding_imsis:
                answers = self.execute_prompt(self.imsi_questions())
                if 'imsi' in answers:
                    try:
                        imsi = json.loads(answers['imsi'])
                        for i in imsi:
                            logging.debug('Adding IMSI: %s', i['imsi'])
                        imsis = None
                        with open('configs/imsis.json', 'r') as f_handle:
                            imsis = json.load(f_handle)
                        imsis += imsi
                        with open('configs/imsis.json', 'w') as f_handle:
                            json.dump(imsis, f_handle, indent=2)
                    except Exception as err:  # pragma: no cover
                        logging.error(
                            'Unable to add IMSI because: %s', err)
                adding_imsis = answers.get('add_imsi', False)

    def main(self):
        """Main entrypoint to the class, parse args and main program driver"""
        self.set_config_dir()
        parser = argparse.ArgumentParser(prog='Daedalus',
                                         description='Daedalus - A tool for creating 4G/5G environments both with SDRs and virtual simulation to run experiments in')
        parser.add_argument('--build', '-b', action='store_true',
                            help='Force build Docker images rather than pulling')
        # TODO set log level
        parser.add_argument('--verbose', '-v', choices=[
                            'DEBUG', 'INFO', 'WARNING', 'ERROR'],
                            default='INFO',
                            help='logging level (default=INFO)')
        parser.add_argument('--version', '-V', action='version',
                            version=f'%(prog)s {__version__}')
        args = parser.parse_args(self.raw_args)
        self.check_commands()
        self.cleanup()
        answers = self.execute_prompt(self.main_questions())
        build_srsran, srsran_lime, build_open5gs, build_ueransim = self.parse_answers(
            answers)
        self.parse_sdrs()
        self.write_imsis()
        if args.build:
            self.build_dockers(srsran=build_srsran, ueransim=build_ueransim,
                               open5gs=build_open5gs, srsran_lime=srsran_lime)
        if 'services' in answers:
            self.start_dovesnap()
            self.create_networks()
            self.start_services()
            self.loop()
        self.reset_cwd()
