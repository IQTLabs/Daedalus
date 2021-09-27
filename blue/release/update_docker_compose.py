#!/usr/bin/env python3
# update docker-compose files with a release version or latest.
import json
import sys
import urllib.request
from collections import OrderedDict

import ruamel.yaml

if len(sys.argv) != 2:
    print("supply release version or 'latest' as an argument")
    sys.exit(1)

version = sys.argv[1]
compose_files = ['../5G/core/core.yml', '../5G/core/ui.yml', '../5G/core/epc.yml',
                 '../5G/core/upn.yml', '../5G/core/db.yml', '../5G/SIMULATED/ueransim-gnb.yml',
                 '../5G/SIMULATED/ueransim-ue.yml', '../5G/SIMULATED/srsran-ue.yml',
                 '../5G/SIMULATED/srsran-enb.yml', '../5G/SDR/limesdr.yml',
                 '../5G/SDR/ettus.yml', '../5G/SDR/bladerf.yml']

for compose_file in compose_files:
    # Broadly preserves formatting.
    yaml = ruamel.yaml.YAML()
    yaml.indent(mapping=2, sequence=2, offset=2)
    dc = ruamel.yaml.round_trip_load(
        open(compose_file).read(), preserve_quotes=True)
    for service, service_config in dc['services'].items():
        image, _ = service_config['image'].split(':')
        if 'iqtlabs' in image:
            service_config['image'] = ':'.join((image, version))
    yaml.dump(dc, open(compose_file, 'w'))
