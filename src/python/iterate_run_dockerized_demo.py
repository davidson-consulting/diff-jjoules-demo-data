import os
import sys

def read_and_delete_docker_id_container():
    id_container = '-1'
    with open(PATH_TO_ID_CONTAINER, 'r') as id_container_file:
        id_container = id_container_file.read()
    run_cmd(' '.join(['rm', '-rf', PATH_TO_ID_CONTAINER]))
    return id_container

def run_cmd(cmd):
    print(cmd)
    os.system(cmd)

PATH_TO_ID_CONTAINER = '/tmp/docker_test.cid'

ITERATION = 100

if __name__ == '__main__':

    id_image = sys.argv[1]
    versions = ['v1', 'v2']
    output_folder = 'target/demo-output/'
    run_cmd(' '.join([
        'mkdir', output_folder
    ]))
    for i in range(0, ITERATION):
        for version in versions:
            run_cmd(' '.join([
                'docker', 'rm', 'diff-jjoules-demo-' + version
            ]))
            run_cmd(' '.join([
                'docker',
                'run',
                '--name',
                'diff-jjoules-demo-' + version,
                '--cidfile', PATH_TO_ID_CONTAINER,
                '--security-opt', 'seccomp=unconfined',
                id_image,
                version,
                str(ITERATION)
            ]))
            id_container = read_and_delete_docker_id_container()
            run_cmd(' '.join([
                'mkdir', output_folder + '/' + str(i)
            ]))
            run_cmd(' '.join([
                'docker',
                'cp',
                id_container + ':' + '/tmp/demo-docker-output/' + version,
                output_folder + '/' + str(i) + '/'
            ]))