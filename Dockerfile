FROM docker.io/axel7083/oasst-inference-worker:v1-1686161777

ENV REMOTE_DEV_TRUST_PROJECTS=1
RUN curl -o pycharm-professional.tar.gz  -L https://download.jetbrains.com/python/pycharm-professional-2023.1.2.tar.gz && tar -xzf pycharm-professional.tar.gz -C /opt && rm pycharm-professional.tar.gz
RUN apt update && apt install openssh-server -y && echo 'root:password' | chpasswd && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config && service ssh start
ENTRYPOINT ["/opt/pycharm-2023.1.2/bin/remote-dev-server.sh", "run", "/worker"]
