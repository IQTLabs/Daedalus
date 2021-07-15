import argparse
import logging
import os
import shlex

from daedalus import __version__
import docker as dclient
from plumbum import local, FG, TF
from plumbum.cmd import cp, curl, docker, docker_compose, ip, ls, mkdir, rm, sudo, tar
from PyInquirer import prompt
from PyInquirer import Separator

from examples import custom_style_2


level_int = {'CRITICAL': 50, 'ERROR': 40, 'WARNING': 30, 'INFO': 20,
             'DEBUG': 10}
level = level_int.get(os.getenv('LOGLEVEL', 'INFO').upper(), 0)
logging.basicConfig(level=level)


class Daedalus():

    def __init__(self, raw_args=None):
        self.compose_files = []
        previous_dir = os.getcwd()
        os.chdir("5G")
        self.main(raw_args=raw_args)
        os.chdir(previous_dir)

    @staticmethod
    def build_dockers(srsran=False, ueransim=False, open5gs=False, srsran_version="release_21_04"):
        if srsran:
            base_args = ["build", "-t", "srsran:base", "-f", "Dockerfile.base", "."]
            srs_args = ["build", "-t", "srsran", "-f", "Dockerfile.srs", "--build-arg", f'SRS_VERSION={srsran_version}', "."]
            with local.cwd(local.cwd / 'srsRAN'):
                docker.bound_command(base_args) & FG
                docker.bound_command(srs_args) & FG
        if ueransim:
            args = ["build", "-t", "ueransim", "."]
            with local.cwd(local.cwd / 'UERANSIM'):
                docker.bound_command(args) & FG
        if open5gs:
            args = ["build", "-t", "open5gs", "."]
            with local.cwd(local.cwd / 'open5gs'):
                docker.bound_command(args) & FG
        return

    @staticmethod
    def start_dovesnap():
        RELEASE = "v0.22.1"
        TPFAUCETPREFIX = "/tmp/tpfaucet"
        sudo[ip["link", "add", "tpmirrorint", "type", "veth", "peer", "name", "tpmirror"]](retcode=(0,2))
        sudo[ip["link", "set", "tpmirrorint", "up"]]()
        sudo[ip["link", "set", "tpmirror", "up"]]()
        sudo[rm["-rf", f'{TPFAUCETPREFIX}']]()
        sudo[rm["-rf", local.cwd // "IQTLabs-dovesnap-*"]]()
        mkdir["-p", f'{TPFAUCETPREFIX}/etc/faucet']()
        cp["configs/faucet/faucet.yaml", f'{TPFAUCETPREFIX}/etc/faucet/']()
        cp["configs/faucet/acls.yaml", f'{TPFAUCETPREFIX}/etc/faucet/']()
        curl["-LJO", f'https://github.com/iqtlabs/dovesnap/tarball/{RELEASE}']()
        tar["-xvf", local.cwd // "IQTLabs-dovesnap-*.tar.gz"]()
        rm[local.cwd // "IQTLabs-dovesnap-*.tar.gz"]()
        args = ["-f", "docker-compose.yml", "-f", "docker-compose-standalone.yml", "up", "-d"]
        dovesnap_dir = local.cwd // 'IQTLabs-dovesnap-*'
        with local.env(MIRROR_BRIDGE_OUT="tpmirrorint", FAUCET_PREFIX=f'{TPFAUCETPREFIX}'):
            with local.cwd(dovesnap_dir[0]):
                docker_compose.bound_command(args) & FG

    @staticmethod
    def create_networks():
        dovesnap_opts = ["network", "create", "-o", "ovs.bridge.controller=tcp:127.0.0.1:6653,tcp:127.0.0.1:6654", "-o", "ovs.bridge.mtu=9000", "--ipam-opt", "com.docker.network.driver.mtu=9000", "--internal"]
        cpn_opts = ["-o", "ovs.bridge.vlan=26", "-o", "ovs.bridge.dpid=0x620", "-o", "ovs.bridge.mode=routed", "--subnet", "192.168.26.0/24", "--gateway", "192.168.26.1", "--ipam-opt", "com.docker.network.bridge.name=cpn", "-o", "ovs.bridge.nat_acl=protectcpn", "-d", "ovs", "cpn"]
        upn_opts = ["-o", "ovs.bridge.vlan=27", "-o", "ovs.bridge.dpid=0x630", "-o", "ovs.bridge.mode=nat", "--subnet", "192.168.27.0/24", "--gateway", "192.168.27.1", "--ipam-opt", "com.docker.network.bridge.name=upn", "-d", "ovs", "upn"]
        rfn_opts = ["-o", "ovs.bridge.vlan=28", "-o", "ovs.bridge.dpid=0x640", "-o", "ovs.bridge.mode=flat", "--subnet", "192.168.28.0/24", "--ipam-opt", "com.docker.network.bridge.name=rfn", "-o", "ovs.bridge.nat_acl=protectrfn", "-d", "ovs", "rfn"]
        ran_opts = ["-o", "ovs.bridge.vlan=29", "-o", "ovs.bridge.dpid=0x650", "-o", "ovs.bridge.mode=routed", "--subnet", "192.168.29.0/24", "--gateway", "192.168.29.1", "--ipam-opt", "com.docker.network.bridge.name=ran", "-o", "ovs.bridge.nat_acl=protectran", "-d", "ovs", "ran"]
        docker.bound_command(dovesnap_opts + cpn_opts) & FG
        docker.bound_command(dovesnap_opts + upn_opts) & FG
        docker.bound_command(dovesnap_opts + rfn_opts) & FG
        docker.bound_command(dovesnap_opts + ran_opts) & FG

    def start_services(self):
        if len(self.compose_files) > 0:
            compose_up = self.compose_files + ["up", "-d", "--build"]
            # TODO don't hardcode the env vars
            with local.env(PRB="50", BLADERF_EARFCN="3400", ETTUS_EARFCN="1800", LIMESDR_EARFCN="900"): 
                docker_compose.bound_command(compose_up) & FG
        else:
            logging.warning('No services to start, quitting.')

    def follow_logs(self):
        if len(self.compose_files) > 0:
            compose_logs = self.compose_files + ["logs", "-f"]
            docker_compose.bound_command(compose_logs) & TF(None, FG=True)
        else:
            logging.warning('No services to log.')

    @staticmethod
    def remove_volumes():
        mongo_args = ["volume", "rm", "-f", "core_mongodb_data"]
        dovesnap_dir = local.cwd // 'IQTLabs-dovesnap-*'
        # TODO volume still might exist even if the directory doesn't
        if len(dovesnap_dir) == 0:
            return
        dovesnap_name = dovesnap_dir[0].split('/')[-1]
        dovesnap_args = ["volume", "rm", "-f", f'{dovesnap_name.lower()}_ovs-data']
        logging.info('Removing volumes')
        try:
            docker.bound_command(mongo_args) & FG
        except Exception as e:
            logging.debug(f'{e}')
        try:
            docker.bound_command(dovesnap_args) & FG
        except Exception as e:
            logging.debug(f'{e}')

    @staticmethod
    def remove_dovesnap():
        args = ["-f", "docker-compose.yml", "-f", "docker-compose-standalone.yml", "down", "--remove-orphans"]
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
        cpn_args = ["network", "rm", "cpn"]
        upn_args = ["network", "rm", "upn"]
        rfn_args = ["network", "rm", "rfn"]
        ran_args = ["network", "rm", "ran"]
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
            compose_down = self.compose_files + ["down", "--remove-orphans"]
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
                    {'name': '4G bladeRF eNodeB (eNB)'},
                    {'name': '4G LimeSDR eNodeB (eNB)'},
                    {'name': '4G Ettus USRP B2xx eNodeB (eNB)'},
                    {'name': '4G srsRAN UE (UE)'},
                    {'name': '5G UERANSIM UE (UE)'},
                    {'name': 'Add UE IMSIs'},
                    {'name': 'Subscriber WebUI'},
                ],
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
        logging.info('Cleaning up any previously running Daedalus environments...')
        client = dclient.from_env()
        containers = client.containers.list(filters={"label": "daedalus.namespace=primary"})

        for container in containers:
            try:
                logging.debug(f'Removing container: {container.name}') 
                container.remove(force=True)
            except Exception as e:
                logging.debug(f'{e}')
        self.remove_networks()
        self.remove_dovesnap()
        self.remove_volumes()

    @staticmethod
    def check_commands():
        logging.info('Checking necessary commands exist, if it fails, install the missing tool and try again.')
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
                    self.remove_volumes()
                if 'Quit (services that were not removed will continue to run)' in selections:
                    running = False

    def main(self, raw_args=None):
        parser = argparse.ArgumentParser(prog='Daedalus',
            description='Daedalus - A tool for creating 4G/5G environments both with SDRs and virtual simulation to run experiments in')
        parser.add_argument('--version', '-V', action='version', version=f'%(prog)s {__version__}')
        parser.add_argument('--verbose', '-v', choices=[
                            'DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO', help='logging level (default=INFO)')
        args = parser.parse_args(raw_args)
        self.check_commands()
        self.cleanup()
        answers = self.execute_prompt(self.main_questions())
        srsran_version = "release_21_04"
        build_srsran = False
        build_open5gs = False
        build_ueransim = False
        ask_prb = False
        ask_earfcn = False
        add_imsis = False
        if 'services' in answers:
            selections = answers['services']
            if '4G Open5GS EPC (HSS, MME, SMF, SGWC, PCRF)' in selections:
                self.compose_files += ['-f', 'core/epc.yml']
                build_open5gs = True
            else:
                logging.warning('No EPC was selected, this configuration is unlikely to work.')
            if 'Open5GS User Plane Network (UPF, SGWU)' in selections:
                self.compose_files += ['-f', 'core/upn.yml']
                build_open5gs = True
            if 'Subscriber Database (MongoDB)' in selections:
                self.compose_files += ['-f', 'core/db.yml']
            else:
                logging.warning('No database was selected, this configuration is unlikely to work.')
            if '5G Open5GS Core (NRF, AUSF, NSSF, UDM, BSF, PCF, UDR, AMF)' in selections:
                self.compose_files += ['-f', 'core/core.yml']
                build_open5gs = True
            if '5G UERANSIM gNodeB (gNB)' in selections:
                self.compose_files += ['-f', 'SIMULATED/ueransim-gnb.yml']
                build_ueransim = True
            if '4G srsRAN eNodeB (eNB)' in selections:
                self.compose_files += ['-f', 'SIMULATED/srsran-enb.yml']
                build_srsran = True
            if '4G bladeRF eNodeB (eNB)' in selections:
                self.compose_files += ['-f', 'SDR/bladerf.yml']
                build_srsran = True
                ask_prb = True
                ask_earfcn = True
            if '4G LimeSDR eNodeB (eNB)' in selections:
                self.compose_files += ['-f', 'SDR/limesdr.yml']
                build_srsran = True
                srsran_version = "release_19_12"
                ask_prb = True
                ask_earfcn = True
            if '4G Ettus USRP B2xx eNodeB (eNB)' in selections:
                self.compose_files += ['-f', 'SDR/ettus.yml']
                from plumbum.cmd import uhd_find_devices
                uhd_find_devices()
                build_srsran = True
                ask_prb = True
                ask_earfcn = True
            if '4G srsRAN UE (UE)' in selections:
                self.compose_files += ['-f', 'SIMULATED/srsran-ue.yml']
                build_srsran = True
            if '5G UERANSIM UE (UE)' in selections:
                self.compose_files += ['-f', 'SIMULATED/ueransim-ue.yml']
                build_ueransim = True
            if 'Add UE IMSIs' in selections:
                add_imsis = True
            if 'Subscriber WebUI' in selections:
                self.compose_files += ['-f', 'core/ui.yml']
                build_open5gs = True
                
            self.build_dockers(srsran=build_srsran, ueransim=build_ueransim, open5gs=build_open5gs, srsran_version=srsran_version)
            self.start_dovesnap()
            self.create_networks()
            self.start_services()
            self.loop()
