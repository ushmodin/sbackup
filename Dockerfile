FROM ubuntu:18.04
RUN apt-get update && apt-get install -y python2.7 \
     python-glade2 \
     python-notify \
     gettext \
     python-setuptools \
     python-gtk2 \
     gvfs \
     gvfs-fuse \
     gvfs-backends \
     curlftpfs \
     python-pexpect \
     python-gconf \
     make \
     dbus-x11 \
     python-dbus \
     openssh-server
VOLUME /sys/fs/cgroup /run /tmp
ENV container=docker