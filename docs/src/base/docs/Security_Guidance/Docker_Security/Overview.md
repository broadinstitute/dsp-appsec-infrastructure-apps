# Attacking Dockers

## Background

One of the biggest changes in the emergence of Docker is a revolution in the application delivery model. Docker can encapsulate the production environment, and can be quickly deployed based on mirroring, dynamic migration and elastic scaling. In the past, if you needed to release an application you must first build an environment in the development environment, install, configure, and then do an installation and configuration in the test environment, then build in the production environment. Amongst numerous benefits that Docker has brought to application delivery, one of the major benefits in terms of operation and maintenance is that it's readable. After using Docker all the configuration done in the production environment is written in a file, such as `Dockerfile, YAML file, etc`. Docker has made a big and disruptive change to the traditional application delivery. 

_**So what are the characteristics of its traditional security solutions?**_ 

* First of all, Docker itself provides a new attack point.
* Secondly, because Docker shares the kernel with the host, it can enter other containers on the host by breaking the kernel, so this also provides a new attack opportunity. 
* Third, Docker itself is a piece of software and vulnerabilities in it present a new challenge. 

_**Docker use**_

The container needs to dispatch the system. If you only used a single Docker, you may enjoy its environment encapsulation and ease of migration. However, after using the container on a large scale, you should care about how its scheduling is done, the then scheduling system is also a new one. This is a point of attack. This new deployment will also have some new impact on traditional security work. 

_**Operation vs Maintenance vs Configuration**_

Finally, containers are not the same in terms of operation and maintenance and configuration, and there are some new security issues. So after the advent of Docker, many new security solutions were challenged. For traditional security, the container is equivalent to a virtual machine. It is an operating environment, so it is more of a security of the traditional base layer to increase the security from the outer layer to the inner layer. Here is no way to talk about how traditional security is done, whether you use containers or virtual machines, the traditional solution is to do. This article mainly talks about how Docker itself is safe.

## Attacker's Mindset

As an Attacker one may think attacking the containers to gain access to the host system, data and assets by:

* Attacking container capabilities
* Attacking insecure volume mounts in containers
* Attacking runtime misconfigurations
* Exploiting docker secrets misconfiguration

## **Security in Docker Containers vs VMs**

One of the many misconceptions on the difference between Docker containers vs VMs is that Docker are actually more secure in terms of preventing some malicious code from affecting other machines, compared to virtual machines or bare metal.   
In general, the security of a virtual machine is better than that of a container. To break through the virtual machine to a host or other virtual machine is extremely difficult through the hypervisor layer. The docker container shares the kernel, file system and other resources with the host, and is more likely to affect other containers and hosts. If someone exploits a kernel bug inside a container it exploits it in the host OS. If this exploit allows for code execution, it will be executed in the host OS, not inside the containers. This is a process that would be much harder and longer in a VM where an attacker would have to exploit both the VM kernel, the hypervisor and the host kernel. ****

![VMs vs Containers](/img/sec_docker_vm.png)

## Docker Threat Modeling

Auditing docker containerized environment from a security perspective involves identifying security misconfigurations while deploying and running docker containers. Auditing docker containers and its runtime environment requires inspecting the following components.

* Docker images
* Docker containers
* Docker networks
* Docker registries
* Docker volumes
* Docker runtime

# Additional Resources for Docker Security

* [OWASP Docker Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
* [OWASP Docker Top 10(in progress)](https://github.com/OWASP/Docker-Security)
* [CIS Docker Benchmark](https://dev-sec.io/baselines/docker/)