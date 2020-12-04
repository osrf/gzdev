#
# Copyright (C) 2029 Open Source Robotics Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Usage:
    gzdev ign-docker-env IGN_RELEASE
                [--linux-distro <linux-distro>]
                [--docker-args DOCKER_ARGS]
    gzdev ign-docker-env -h | --help
    gzdev ign-docker-env --version

Options:
    -h --help                   Show this screen
    --version                   Show gzdev's version
    --linux-distro=linux-distro Linux distibution to use in docker env
    --docker-args DOCKER_ARGS   Extra arguments to pass to docker
"""

from docopt import docopt
from subprocess import check_call
from sys import stderr
import os


ROCKER_CMD = ['rocker', '--x11', '--user']


def detect_nvidia():
    return [x for x in os.listdir('/dev/') if x.startswith('nvidia')] != []


def _check_call(cmd):
    print('')
    print("Invoking '%s'" % ' '.join(cmd))
    print('')

    try:
        check_call(cmd)
    except Exception as e:
        print(str(e))


def error(msg):
    print(f"\n {msg} \n", file=stderr)
    exit(-1)


# TODO: use a yaml file to get this information
def default_distro_by_ignition(ignition_release):
    if ignition_release == 'dome':
        return 'ubuntu:focal'
    elif ignition_release == 'citadel':
        return 'ubuntu:bionic'
    else:
        error(f"Unknown ignition release {ignition_release}")


def build_rocker_command(igniton_release, linux_distro, docker_args):
    _, linux_distro_release = linux_distro.split(':')
    cmd = ROCKER_CMD + ['--nvidia'] if detect_nvidia() else ROCKER_CMD
    cmd += ['--ignition', f"{igniton_release}:{linux_distro_release}"]
    cmd += docker_args if docker_args else []
    cmd += ['--']
    cmd += [linux_distro, '/bin/bash']
    return cmd


def normalize_args(args):
    if not args['IGN_RELEASE']:
        error('The plugin must be run using the --ignition flag')
    ignition_version = args['IGN_RELEASE']

    if args['--linux-distro']:
        linux_distro = args['--linux-distro']
    else:
        linux_distro = default_distro_by_ignition(ignition_version)

    docker_args = args['--docker-args'].split(' ') if args['--docker-args'] else None

    return ignition_version, linux_distro, docker_args


def main():
    try:
        ignition_version, linux_distro, docker_args = normalize_args(docopt(__doc__, version="gzdev-docker-env 0.1.0"))
        rocker_cmd = build_rocker_command(ignition_version, linux_distro, docker_args)
        check_call(rocker_cmd)
    except KeyboardInterrupt:
        print("docker-env was stopped with a Keyboard Interrupt.\n")


if __name__ == '__main__':
    main()
