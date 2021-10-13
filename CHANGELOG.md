# v0.8.1 (2021-10-13)

* Upgrade Open5GS to 2.3.4
* Upgrade UHD to v4.1.0.3
* Upgrade docker, dovesnap, pylint, pytype, pytest

# v0.8.0 (2021-09-02)

* Fixed an issue where permissions under /usr could potentially get trashed
* Reduced the image size for Open5GS by half
* Updated docker, docker-compose, plumbum, pylint, pytest-cov, pytest, pytype, ruamel.yaml
* Added some more docs

# v0.7.4 (2021-09-01)

* Use versionsed base image for srsRAN
* Change cmake flags to allow for srsRAN to run on CPUs that don't have AVX512
* Add iot.nb APN and fallback subnet for unknown APNs

# v0.7.3 (2021-08-31)

* Remove unnecessary configs
* Fix interfaces for different APNs
* Add a healthcheck for mongoloader successfully importing IMSI records
* Add virtual UE internet connectivity integration tests for both eNB and gNB setups

# v0.7.2 (2021-08-27)

* Reduce number of things UHD installs and downloads for quicker build times and smaller image sizes

# v0.7.1 (2021-08-27)

* Fix scripts not being executable

# v0.7.0 (2021-08-26)

* Updated Open5GS
* Updated uhd for Ettus
* Updated dovesnap, and locked to versions for pulling images rather than building
* Using a versioned UERANSIM now
* Consolidated configs into a single file slice.yaml for most components
* Added tests
* Uses versioned images for pulling rather than building
* Added option to still build images if preferred
* Consolidated scripts to reduce duplication
* Added a healthcheck for the NRF for services registered with it
* Added a healthcheck for MongoDB
* Moved to one SGWU and one UPF to simplify configs

# v0.6.0 (2021-07-27)

* Pinned MongoDB version for loader
* Updated Dovesnap
* Updated precommit hooks
* Added Maintainer labels
* Add Docker image builds to workflows
* Linting

# v0.5.1 (2021-07-23)

* Fix name of LimeSDR PRB variable

# v0.5.0 (2021-07-23)

* Fix incorrect handling of PRB and EARFCN options for Ettus and BladeRF
* Dynamically generate certs instead of using static ones in the repo

# v0.4.0 (2021-07-20)

* Implement adding IMSIs through the CLI

# v0.3.0 (2021-07-19)

* Enable configurable PRB and EARFCN per SDR
* Allow LimeSDR and other SDRs to work together despite different versions of srsRAN
* Updated Open5GS to 2.3.2
* Added additional exception handling

# v0.2.0 (2021-07-16)

* Cleanup anonymous volumes from services when removing the services
* Allow SMF to work with or without NRF
* Lock MongoDB to a version

# v0.1.5 (2021-07-15)

* Fixed permissions

# v0.1.4 (2021-07-15)

* Fixed data file path

# v0.1.3 (2021-07-15)

* Fixed data file path

# v0.1.2 (2021-07-15)

* Fixed bug with bad version

# v0.1.1 (2021-07-15)

* Fixed bug with bad version

# v0.1.0 (2021-07-15)

* Initial tool published to PyPi
* Enables building required packages for Open5GS, srsRAN, UERANSIM
* Can run a 4G and 5G core, 4G eNB simulated, 4G UE simulated, 5G gNB simulated, 5G UE simulated
* Supports the following SDRs: BladeRF, LimeSDR, and Ettus USRP B200
