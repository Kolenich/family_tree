#!/bin/sh

docker build -t family_tree .
docker tag family_tree kolenich/family_tree
docker push kolenich/family_tree