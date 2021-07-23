# Security Guidelines

The aim of these generic security guidelines is to provide an easy to use list of common security mistakes and good practices around securing Docker containers.

### **1. Keep Host and Docker always up to date** 

### **2. Do not expose the docker Daemon socket(even to the containers)**

* [x] Do not enable tcp Docker daemon socket. If you are running docker daemon with **`-H tcp://0.0.0.0:XXX`** or similar you are exposing un-encrypted and un-authenticated direct access to the Docker daemon. If you really, really have to do this you should secure it. Check how to do this [following Docker official documentation](https://docs.docker.com/engine/reference/commandline/dockerd/#daemon-socket-option). ****
* [x] **Do not expose `/var/run/docker.sock` to other containers**. If you are running your docker image with `-v /var/run/docker.sock://var/run/docker.sock` or similar you should change it. Remember that mounting the socket read-only is not a solution but only makes it harder to exploit. Equivalent in docker-compose file is something like this

  ```text
  volumes:
  - "/var/run/docker.sock:/var/run/docker.sock"
  ```

### **3. Set a user** 

Configuring container, to use unprivileged user, is the best way to prevent privilege escalation attacks. This can be accomplished in three different ways:

* **Build Time**

  ```text
  FROM alpine
  RUN groupadd -r myuser && useradd -r -g myuser myuser
  <HERE DO WHAT YOU HAVE TO DO INSTALLING PACKAGES ETC.>
  USER myuser

  ```

* **Runtime**

  ```text
  docker run -u 4000 alpine
  ```


### 4. Limit capabilities <a id="rule-3---limit-capabilities-grant-only-specific-capabilities-needed-by-a-container"></a>

_Grant only specific capabilities needed by a container_

\*\*\*\*[Linux kernel capabilities](http://man7.org/linux/man-pages/man7/capabilities.7.html) are set of privileges that can be used by privileged. Docker, by default, runs with only a subset of capabilities. You can change it and drop some capabilities(using **`--cap-drop`**) to harden your docker containers, or add some capabilities(using **`--cap-add`**) if needed. Remember not to run containers with the **`--privileged`** flag **-** this will add ALL Linux kernel capabilities to the container

The most secure setup is to drop all capabilities **`--cap-drop all`** and then add only required ones. For example:

```text
docker run --cap-drop all --cap-add CHOWN alpine
```
### 5. Disable inter-container communication

By default inter-container communication(icc) is enabled - it means that all containers can talk with each other(using [`docker0` bridged network](https://docs.docker.com/v17.09/engine/userguide/networking/default_network/container-communication/#communication-between-containers)). This can be disabled by running docker daemon with **`--icc=false`** flag. If icc is disabled(icc=false) it is required to tell which containers can communicate using **`--link=CONTAINER_NAME_or_ID:ALIAS`** option. See more in [Docker documentation - container communication](https://docs.docker.com/v17.09/engine/userguide/networking/default_network/container-communication/#communication-between-containers)

In Kubernetes [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/) can be used for it.

### 6. Set filesystem and volumes to read-only <a id="rule-8---set-filesystem-and-volumes-to-read-only"></a>

**Run containers with a read-only filesystem** using `--read-only` flag. For example:

```text
docker run --read-only alpine sh -c 'echo "whatever" > /tmp'
```

If application inside container have to save something temporarily combine `--read-only` flag with `--tmpfs` like this:

```text
docker run --read-only --tmpfs /tmp alpine sh -c 'echo "whatever" > /tmp/file'
```

Equivalent in docker-compose file will be:

```text
version: "3"
services:
  alpine:
    image: alpine
    read_only: true
```

Equivalent in Kubernetes in [Security Context](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) will be:

```text
kind: ...
apiVersion: ...
metadata:
  name: ...
spec:
  ...
  containers:
  - name: ...
    image: ....
    securityContext:
          ...
          readOnlyRootFilesystem: true
          ...
```

In addition if volume is mounted only for reading **mount them as a read-only** It can be done by appending `:ro` to the `-v` like this:

```text
docker run -v volume-name:/path/in/container:ro alpine
```

Or by using `--mount` option:

```text
docker run --mount source=volume-name,destination=/path/in/container,readonly alpine
```

### 7. Set the logging level to at least INFO <a id="rule-10---set-the-logging-level-to-at-least-info"></a>

By default, the Docker daemon is configured to have a base logging level of `info`, and if this is not the case: set the Docker daemon log level to 'info'.   
**Rationale:** Setting up an appropriate log level, configures the Docker daemon to log events that you would want to review later. A base log level of 'info' and above would capture all logs except debug logs. Until and unless required, you should not run docker daemon at 'debug' log level.

To configure the log level in docker-compose:

```text
$ docker-compose --log-level info up
```

#### References

* [Google on Securing containers](https://docs.google.com/document/d/1QQ5u1RBDLXWvC8K3pscTtTRThsOeBSts_imYEoRyw8A/edit#heading=h.ypyhxoaw8f95)
* \*\*\*\*[Docker Baselines on DevSec](https://dev-sec.io/baselines/docker/)
* [Use the Docker command line](https://docs.docker.com/engine/reference/commandline/cli/)
* [Overview of docker-compose CLI](https://docs.docker.com/compose/reference/overview/)
* [Configuring Logging Drivers](https://docs.docker.com/config/containers/logging/configure/)
* [View logs for a container or service](https://docs.docker.com/config/containers/logging/)