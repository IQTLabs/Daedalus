Daedalus
==========

A 5G core network can experience attacks from the radio (RAN) and the Data-Network side of the architecture. In most cases, the defense strategy for a 5G core-network is similar to that of securing an enterprise network. However, there are subtle differences between a 5G and an enterprise network that make the defenses different for each.

This project explores mechanisms to make informed decisions from a variety of response options that can be used to mitigate attack effectiveness by steering malicious actors to domains that the defender can better control for securing a 5G core-network.

We have developed a set of attack classes and defense responses designed to achieve various outcomes in the way that the attacker exploits the network. These scenarios are listed in the matrix below.

<img src = "images/daedalus-grid-5g.png" width=600>

We have identified five key modes of attack. They are
* reconaissance and discovery: gaining knowledge about a network
* theft and exfiltration: unauthorized removal data/information
* access and privilege escalation: gaining unauthorized access to the network
* destruction: destruction of data, information or anything needed for the network to function
* denial and disruption: preventing or degrading services and access to the network by authorized users

Alternatetively, each of these attack modes can be countered with one of the following defenese responses:
* none: do nothing
* denial and fire-walling: denying/blocking network access to the attacker
* deception: trick the attacker to steal information of little to no value
* degradation: reduce the attackers effectiveness by breaking up data so it is not available all in one place
* quarantine and isolation: contain the attack to a portion of the network that is easier to defend or has little value
* throttling: significantly increase the amount of time the attacker needs to achieve objectives

We use the Red-Team/Blue-Team approach where the red-team serves as the attacker and the blue-team as the defender. The red-team has minimal knowledge of blue-team defenses as it develops an attack strategy. The blue-team is passive in the attack exercises, only recording what is needed to reproduce the scenario. The goal is not to necessarily develop new exploits, but rather to use known exploits, tools and techniques to navigate the attack surface.
