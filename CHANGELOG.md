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
