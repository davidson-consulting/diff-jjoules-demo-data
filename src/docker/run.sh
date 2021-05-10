#!/bin/sh

version_folder=${1}
iteration=${2}

LD_LIBRARY_PATH=/tmp/junit-jjoules/src/main/c/lib/
export LD_LIBRARY_PATH
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

rm -rf /tmp/demo-docker-output/
mkdir /tmp/demo-docker-output/
mkdir /tmp/demo-docker-output/${version_folder}

for i in $(seq 1 ${iteration}); do
    echo ${i} / ${iteration}
    mvn -Drat.skip=true -Djacoco.skip=true -Danimal.sniffer.skip=true -f  /tmp/${version_folder}/pom.xml test -Dtest=fr.davidson.diff_jjoules_demo.InternalListTest#aaa_0_testMapOneElement+aaa_1_testMapOneElement+aaa_2_testMapOneElement+aaa_3_testMapOneElement+aaa_4_testMapOneElement+testMapOneElement+aaa_0_testMapMultipleElement+aaa_1_testMapMultipleElement+aaa_2_testMapMultipleElement+aaa_3_testMapMultipleElement+aaa_4_testMapMultipleElement+testMapMultipleElement+aaa_0_testMapEmptyList+aaa_1_testMapEmptyList+aaa_2_testMapEmptyList+aaa_3_testMapEmptyList+aaa_4_testMapEmptyList+testMapEmptyList --quiet
    cp -r /tmp/${version_folder}/target/jjoules-reports /tmp/demo-docker-output/${version_folder}/${i}
done
