# Namespaces

Docker uses namespaces to provide the isolated workspace called the container. When you run a container, Docker creates a set of namespaces for that container.

* The **`pid`** namespace: Process isolation(_PID: Process ID_)
* The **`net`** namespace: Managing network interfaces(_NET_: _Networking_)
* The **`ipc`** namespace: Managing access to IPC resources(_IPC_: _InterProcess_ _Communication_)
* The **`mnt`** namespace: Managing filesystem mount points(_MNT: Mount_)
* The **`uts`** namespace: Different host and domain names(_UTS: Unix Timesharing System_)
* The **`user`** namespace: Isolate security-related identifiers(_USER: userid, groupid_)

```text
docker run --rm -d alpine sleep 1111

ps auxx | grep 'sleep 1111'

sudo ls /proc/[pid]/ns/
```

#### PID namespace

* PID namespaces isolate the process ID number space, meaning that processes in different PID namespaces can have the same PID
* PID namespaces allow containers to provide functionality such as suspending/resuming the set of processes in the container and migrating the container to a new host while the processes inside the container maintain the same PIDs

> For example, while running `nginx` docker container we always get PID 1 for `nginx` but at the host we see a different PID like `9989`

```text
docker run --rm --name=example -d nginx:alpine
ps auxxx | grep nginx

docker exec -it example sh
ps auxxx | grep nginx
```

#### Attaching host processes to container

* We can also pass or attach the host process namespace or any other container process namespace to container using the --pid flag

```text
docker run --rm -it --pid=host some/image
```