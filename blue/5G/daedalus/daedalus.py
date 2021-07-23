import argparse
import json
import logging
import os
import shlex
import sys

import docker as dclient
from daedalus import __file__
from daedalus import __version__
from daedalus.validators import IMSIValidator
from daedalus.validators import NumberValidator
from examples import custom_style_2
from plumbum import FG
from plumbum import local
from plumbum import TF
from plumbum.cmd import chmod
from plumbum.cmd import cp
from plumbum.cmd import curl
from plumbum.cmd import docker
from plumbum.cmd import docker_compose
from plumbum.cmd import ip
from plumbum.cmd import ls
from plumbum.cmd import mkdir
from plumbum.cmd import rm
from plumbum.cmd import sudo
from plumbum.cmd import tar
from PyInquirer import prompt
from PyInquirer import Separator


level_int = {'CRITICAL': 50, 'ERROR': 40, 'WARNING': 30, 'INFO': 20,
             'DEBUG': 10}
level = level_int.get(os.getenv('LOGLEVEL', 'INFO').upper(), 0)
logging.basicConfig(level=level)


class Daedalus():

    def __init__(self, raw_args=None):
        self.compose_files = []
        self.options = []
        previous_dir = os.getcwd()
        try:
            os.chdir(os.path.dirname(__file__).split('lib')[0] + '/5G')
            # TODO find a better way to do this for writing out dovesnap files
            sudo[chmod['-R', '777', '.']]()
        except Exception as e:
            logging.error(f'Unable to find config files, exiting because: {e}')
            sys.exit(1)
        self.main(raw_args=raw_args)
        # TODO find a better way to do this for writing out dovesnap files
        sudo[chmod['-R', '755', '.']]()
        os.chdir(previous_dir)

    @staticmethod
    def build_dockers(srsran=False, ueransim=False, open5gs=False, srsran_lime=False):
        if srsran:
            srsran_version = 'release_21_04'
            base_args = ['build', '-t', 'srsran:base',
                         '-f', 'Dockerfile.base', '.']
            srs_args = ['build', '-t', 'srsran', '-f', 'Dockerfile.srs',
                        '--build-arg', f'SRS_VERSION={srsran_version}', '.']
            with local.cwd(local.cwd / 'srsRAN'):
                docker.bound_command(base_args) & FG
                docker.bound_command(srs_args) & FG
        if srsran_lime:
            srsran_version = 'release_19_12'
            srs_args = ['build', '-t', 'srsran-lime', '-f', 'Dockerfile.srs',
                        '--build-arg', f'SRS_VERSION={srsran_version}', '.']
            with local.cwd(local.cwd / 'srsRAN'):
                docker.bound_command(srs_args) & FG
        if ueransim:
            args = ['build', '-t', 'ueransim', '.']
            with local.cwd(local.cwd / 'UERANSIM'):
                docker.bound_command(args) & FG
        if open5gs:
            args = ['build', '-t', 'open5gs', '.']
            with local.cwd(local.cwd / 'open5gs'):
                docker.bound_command(args) & FG
        return

    @staticmethod
    def start_dovesnap():
        RELEASE = 'v0.22.2'
        TPFAUCETPREFIX = '/tmp/tpfaucet'
        sudo[ip['link', 'add', 'tpmirrorint', 'type', 'veth',
                'peer', 'name', 'tpmirror']](retcode=(0, 2))
        sudo[ip['link', 'set', 'tpmirrorint', 'up']]()
        sudo[ip['link', 'set', 'tpmirror', 'up']]()
        sudo[rm['-rf', f'{TPFAUCETPREFIX}']]()
        sudo[rm['-rf', local.cwd // 'IQTLabs-dovesnap-*']]()
        mkdir['-p', f'{TPFAUCETPREFIX}/etc/faucet']()
        cp['configs/faucet/faucet.yaml', f'{TPFAUCETPREFIX}/etc/faucet/']()
        cp['configs/faucet/acls.yaml', f'{TPFAUCETPREFIX}/etc/faucet/']()
        curl['-LJO',
             f'https://github.com/iqtlabs/dovesnap/tarball/{RELEASE}']()
        tar['-xvf', local.cwd // 'IQTLabs-dovesnap-*.tar.gz']()
        rm[local.cwd // 'IQTLabs-dovesnap-*.tar.gz']()
        args = ['-f', 'docker-compose.yml', '-f',
                'docker-compose-standalone.yml', 'up', '-d']
        dovesnap_dir = local.cwd // 'IQTLabs-dovesnap-*'
        with local.env(MIRROR_BRIDGE_OUT='tpmirrorint', FAUCET_PREFIX=f'{TPFAUCETPREFIX}'):
            with local.cwd(dovesnap_dir[0]):
                docker_compose.bound_command(args) & FG

    @staticmethod
    def create_networks():
        dovesnap_opts = ['network', 'create', '-o', 'ovs.bridge.controller=tcp:127.0.0.1:6653,tcp:127.0.0.1:6654',
                         '-o', 'ovs.bridge.mtu=9000', '--ipam-opt', 'com.docker.network.driver.mtu=9000', '--internal']
        cpn_opts = ['-o', 'ovs.bridge.vlan=26', '-o', 'ovs.bridge.dpid=0x620', '-o', 'ovs.bridge.mode=routed', '--subnet', '192.168.26.0/24',
                    '--gateway', '192.168.26.1', '--ipam-opt', 'com.docker.network.bridge.name=cpn', '-o', 'ovs.bridge.nat_acl=protectcpn', '-d', 'ovs', 'cpn']
        upn_opts = ['-o', 'ovs.bridge.vlan=27', '-o', 'ovs.bridge.dpid=0x630', '-o', 'ovs.bridge.mode=nat', '--subnet',
                    '192.168.27.0/24', '--gateway', '192.168.27.1', '--ipam-opt', 'com.docker.network.bridge.name=upn', '-d', 'ovs', 'upn']
        rfn_opts = ['-o', 'ovs.bridge.vlan=28', '-o', 'ovs.bridge.dpid=0x640', '-o', 'ovs.bridge.mode=flat', '--subnet',
                    '192.168.28.0/24', '--ipam-opt', 'com.docker.network.bridge.name=rfn', '-o', 'ovs.bridge.nat_acl=protectrfn', '-d', 'ovs', 'rfn']
        ran_opts = ['-o', 'ovs.bridge.vlan=29', '-o', 'ovs.bridge.dpid=0x650', '-o', 'ovs.bridge.mode=routed', '--subnet', '192.168.29.0/24',
                    '--gateway', '192.168.29.1', '--ipam-opt', 'com.docker.network.bridge.name=ran', '-o', 'ovs.bridge.nat_acl=protectran', '-d', 'ovs', 'ran']
        docker.bound_command(dovesnap_opts + cpn_opts) & FG
        docker.bound_command(dovesnap_opts + upn_opts) & FG
        docker.bound_command(dovesnap_opts + rfn_opts) & FG
        docker.bound_command(dovesnap_opts + ran_opts) & FG

    def start_services(self):
        if len(self.compose_files) > 0:
            compose_up = self.compose_files + ['up', '-d', '--build']
            SMF = ''
            if 'core' in self.options:
                SMF = '5GC'
            # TODO handle multiple SDRs of the same type
            with local.env(BLADERF_PRB=self.bladerf_prb, BLADERF_EARFCN=self.bladerf_earfcn, ETTUS_PRB=self.ettus_prb, ETTUS_EARFCN=self.ettus_earfcn, LIMESDR_PRB=self.limesdr_prb, LIMESDR_EARFCN=self.limesdr_earfcn, SMF=SMF):
                docker_compose.bound_command(compose_up) & FG
        else:
            logging.warning('No services to start, quitting.')

    def follow_logs(self):
        if len(self.compose_files) > 0:
            compose_logs = self.compose_files + ['logs', '-f']
            docker_compose.bound_command(compose_logs) & TF(None, FG=True)
        else:
            logging.warning('No services to log.')

    @staticmethod
    def remove_dovesnap():
        args = ['-f', 'docker-compose.yml', '-f', 'docker-compose-standalone.yml',
                'down', '--volumes', '--remove-orphans']
        dovesnap_dir = local.cwd // 'IQTLabs-dovesnap-*'
        if len(dovesnap_dir) == 0:
            return
        with local.cwd(dovesnap_dir[0]):
            logging.debug('Removing Dovesnap services')
            try:
                docker_compose.bound_command(args) & FG
            except Exception as e:
                logging.debug(f'{e}')

    @staticmethod
    def remove_networks():
        cpn_args = ['network', 'rm', 'cpn']
        upn_args = ['network', 'rm', 'upn']
        rfn_args = ['network', 'rm', 'rfn']
        ran_args = ['network', 'rm', 'ran']
        try:
            logging.info('Removing cpn network')
            docker.bound_command(cpn_args) & FG
        except Exception as e:
            logging.debug(f'{e}')
        try:
            logging.info('Removing upn network')
            docker.bound_command(upn_args) & FG
        except Exception as e:
            logging.debug(f'{e}')
        try:
            logging.info('Removing rfn network')
            docker.bound_command(rfn_args) & FG
        except Exception as e:
            logging.debug(f'{e}')
        try:
            logging.info('Removing ran network')
            docker.bound_command(ran_args) & FG
        except Exception as e:
            logging.debug(f'{e}')

    def remove_services(self):
        if len(self.compose_files) > 0:
            logging.debug('Removing Daedalus services')
            compose_down = self.compose_files + \
                ['down', '--volumes', '--remove-orphans']
            try:
                docker_compose.bound_command(compose_down) & FG
            except Exception as e:
                logging.debug(f'{e}')
        else:
            logging.warning('No services to remove.')

    @staticmethod
    def execute_prompt(questions):
        answers = prompt(questions, style=custom_style_2)
        return answers

    @staticmethod
    def main_questions():
        return [
            {
                'type': 'checkbox',
                'name': 'services',
                'message': 'What services would you like to start?',
                'choices': [
                    {'name': '4G Open5GS EPC (HSS, MME, SMF, SGWC, PCRF)',
                     'checked': True},
                    {'name': 'Open5GS User Plane Network (UPF, SGWU)',
                     'checked': True},
                    {'name': 'Subscriber Database (MongoDB)',
                     'checked': True},
                    {'name': '5G Open5GS Core (NRF, AUSF, NSSF, UDM, BSF, PCF, UDR, AMF)'},
                    {'name': '5G UERANSIM gNodeB (gNB)'},
                    {'name': '4G srsRAN eNodeB (eNB)'},
                    {'name': '4G BladeRF eNodeB (eNB)'},
                    {'name': '4G Ettus USRP B2xx eNodeB (eNB)'},
                    {'name': '4G LimeSDR eNodeB (eNB)'},
                    {'name': '4G srsRAN UE (UE)'},
                    {'name': '5G UERANSIM UE (UE)'},
                    {'name': 'Add UE IMSIs'},
                    {'name': 'Subscriber WebUI'},
                ],
            },
        ]

    @staticmethod
    def sdr_questions(enb):
        return [
            {
                'type': 'list',
                'name': 'prb',
                'message': f'Number of Physical Resource Blocks (PRB) for {enb}',
                'choices': ['6', '15', '25', '50', '75', '100'],
                'default': '50',
            },
            {
                'type': 'input',
                'name': 'earfcn',
                'message': f'What EARFCN code for DL for {enb} would you like?',
                'default': '3400',
                # TODO should also validate the EARFCN wasn't already used
                'validate': NumberValidator,
                'filter': lambda val: int(val),
            },
        ]

    @staticmethod
    def imsi_questions():
        example_imsi = json.loads('''[{
    "access_restriction_data": 32,
    "ambr": {
      "downlink": {
        "unit": 3,
        "value": 1
      },
      "uplink": {
        "unit": 3,
        "value": 1
      }
    },
    "imsi": "001010000000012",
    "network_access_mode": 2,
    "security": {
      "amf": "8000",
      "k": "c8eba87c1074edd06885cb0486718341",
      "op": null,
      "opc": "17b6c0157895bcaa1efc1cef55033f5f"
    },
    "slice": [
      {
        "default_indicator": true,
        "sd": "000000",
        "session": [
          {
            "ambr": {
              "downlink": {
                "unit": 3,
                "value": 1
              },
              "uplink": {
                "unit": 3,
                "value": 1
              }
            },
            "name": "internet",
            "pcc_rule": [],
            "qos": {
              "arp": {
                "pre_emption_capability": 1,
                "pre_emption_vulnerability": 1,
                "priority_level": 8
              },
              "index": 9
            },
            "type": 1
          }
        ],
        "sst": 1
      }
    ],
    "subscribed_rau_tau_timer": 12,
    "subscriber_status": 0
  }]''')

        return [
            {
                'type': 'editor',
                'name': 'imsi',
                'message': 'Add a new IMSI (an example will be prepopulated to get you started)',
                'default': f'{json.dumps(example_imsi, indent=2)}',
                'eargs': {
                    'editor': 'nano',
                    'ext': '.json',
                },
                'validate': IMSIValidator,
            },
            {
                'type': 'confirm',
                'message': 'Would you like to add another IMSI?',
                'name': 'add_imsi',
                'default': False,
            },
        ]

    @staticmethod
    def running_questions():
        return [
            {
                'type': 'list',
                'name': 'actions',
                'message': 'Services have started, what would you like to do?',
                'choices': [
                    {'name': 'Follow logs (Ctrl-c to return to this menu)'},
                    {'name': 'Remove services'},
                    {'name': 'Quit (services that were not removed will continue to run)'},
                ],
            },
        ]

    def cleanup(self):
        logging.info(
            'Cleaning up any previously running Daedalus environments...')
        client = dclient.from_env()
        containers = client.containers.list(
            filters={'label': 'daedalus.namespace=primary'})

        for container in containers:
            try:
                logging.debug(f'Removing container: {container.name}')
                container.remove(force=True)
            except Exception as e:
                logging.debug(f'{e}')
        self.remove_networks()
        self.remove_dovesnap()

    @staticmethod
    def check_commands():
        logging.info(
            'Checking necessary commands exist, if it fails, install the missing tool and try again.')
        chmod['--version']()
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

    def main(self, raw_args=None):
        parser = argparse.ArgumentParser(prog='Daedalus',
                                         description='Daedalus - A tool for creating 4G/5G environments both with SDRs and virtual simulation to run experiments in')
        parser.add_argument('--version', '-V', action='version',
                            version=f'%(prog)s {__version__}')
        parser.add_argument('--verbose', '-v', choices=[
                            'DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO', help='logging level (default=INFO)')
        args = parser.parse_args(raw_args)
        self.check_commands()
        self.cleanup()
        answers = self.execute_prompt(self.main_questions())
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
            if '4G BladeRF eNodeB (eNB)' in selections:
                self.compose_files += ['-f', 'SDR/bladerf.yml']
                self.options.append('bladerf-enb')
                build_srsran = True
            if '4G Ettus USRP B2xx eNodeB (eNB)' in selections:
                self.compose_files += ['-f', 'SDR/ettus.yml']
                self.options.append('ettus-enb')
                from plumbum.cmd import uhd_find_devices
                try:
                    uhd_find_devices()
                except Exception as e:
                    logging.error(
                        'No UHD device found, but you chose Ettus. It is unlikely to work as expected.')
                build_srsran = True
            if '4G LimeSDR eNodeB (eNB)' in selections:
                self.compose_files += ['-f', 'SDR/limesdr.yml']
                self.options.append('limesdr-enb')
                srsran_lime = True
            if '4G srsRAN UE (UE)' in selections:
                self.compose_files += ['-f', 'SIMULATED/srsran-ue.yml']
                self.options.append('srsran-ue')
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

            # defaults
            self.bladerf_prb = '50'
            self.ettus_prb = '50'
            self.limesdr_prb = '50'
            self.bladerf_earfcn = '3400'
            self.ettus_earfcn = '1800'
            self.limesdr_earfcn = '900'
            sdrs = ['limesdr-enb', 'ettus-enb', 'bladerf-enb']
            for sdr in sdrs:
                if sdr in self.options:
                    answers = self.execute_prompt(self.sdr_questions(sdr))
                    if 'prb' in answers:
                        if sdr == 'bladerf-enb':
                            self.limesdr_prb = str(answers['prb'])
                        if sdr == 'ettus-enb':
                            self.limesdr_prb = str(answers['prb'])
                        if sdr == 'limesdr-enb':
                            self.limesdr_prb = str(answers['prb'])
                    if 'earfcn' in answers:
                        if sdr == 'bladerf-enb':
                            self.limesdr_earfcn = str(answers['earfcn'])
                        if sdr == 'ettus-enb':
                            self.limesdr_earfcn = str(answers['earfcn'])
                        if sdr == 'limesdr-enb':
                            self.limesdr_earfcn = str(answers['earfcn'])
            if 'imsis' in self.options:
                adding_imsis = True
                while adding_imsis:
                    answers = self.execute_prompt(self.imsi_questions())
                    if 'imsi' in answers:
                        try:
                            imsi = json.loads(answers['imsi'])
                            for i in imsi:
                                logging.debug(f'Adding IMSI: {i["imsi"]}')
                            imsis = None
                            with open('configs/imsis.json', 'r') as f:
                                imsis = json.load(f)
                            imsis += imsi
                            with open('configs/imsis.json', 'w') as f:
                                json.dump(imsis, f, indent=2)
                        except Exception as e:
                            logging.error(f'Unable to add IMSI because: {e}')
                    if 'add_imsi' in answers:
                        adding_imsis = answers['add_imsi']
            self.build_dockers(srsran=build_srsran, ueransim=build_ueransim,
                               open5gs=build_open5gs, srsran_lime=srsran_lime)
            self.start_dovesnap()
            self.create_networks()
            self.start_services()
            self.loop()
