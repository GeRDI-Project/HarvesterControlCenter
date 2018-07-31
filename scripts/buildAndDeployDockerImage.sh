##!/usr/bin/env bash
#!/bin/bash
# Copyright 2018 Tobias Weber, Jan Frömberg
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

branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$branch" = "master" ]
then
    dockerRegistry="docker-registry.gerdi.research.lrz.de:5043"
    imageName="harvest/hccenter"
    imageUrl="${dockerRegistry}/${imageName}"

    docker build -t "${imageUrl}:latest" .
    docker push "${imageUrl}:latest"

    gittags=$(git tag -l --points-at HEAD)
    if [ ! -z "$gittags" ]
    then
        for gittag in $gittags
        do
            docker tag "${imageUrl}" "${imageUrl}:${gittag}"
            docker push "${imageUrl}:${gittag}"
        done
    fi
else
    echo "On branch $branch - will not build (open a PR to master to build and deploy)"
fi