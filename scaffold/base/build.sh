#!/usr/bin/env bash
set -x

project_root=$(pwd -P 2>/dev/null || command pwd)
while [ ! -e "$project_root/base" ]; do
  project_root=${project_root%/*}
  if [ "$project_root" = "" ]; then break; fi
done

# shellcheck disable=SC1090
source "${project_root}/setenv.sh"

if [[ -z ${KRULES_ROOT_DIR} ]]; then
  echo "KRULES_ROOT_DIR not set"
  exit 1
fi
if [[ -z ${DOCKER_REGISTRY} ]]; then
  echo "DOCKER_REGISTRY not set"
  exit 1
fi


if [[ -z ${PROJECT} ]]; then
  echo "PROJECT not set"
  exit 1
fi


#PROJECT="$( basename $project_root )"

NAME=${PROJECT}-base

bumpversion --current-version "$(cat VERSION)" patch VERSION --allow-dirty
VERSION=$(cat VERSION)

IMAGE_BASE=krules-image-base-dev
IMAGE_BASE_DIR=${KRULES_ROOT_DIR}/${IMAGE_BASE}
BASE_VERSION=$(cat "${IMAGE_BASE_DIR}"/VERSION)

mkdir -p .t_commonlib

rsync -r ${KRULES_ROOT_DIR}/krules-cloudstorage/ .t_commonlib/krules-cloudstorage/
rsync -r ${KRULES_ROOT_DIR}/krules-mongodb/ .t_commonlib/krules-mongodb/

docker build -t "${DOCKER_REGISTRY}"/${NAME}:"${VERSION}" -f- . <<EOF
FROM ade8850/${IMAGE_BASE}:${BASE_VERSION}

ADD .t_commonlib /
RUN python /krules-cloudstorage/setup.py install
RUN mv /krules-cloudstorage/krules_cloudstorage app/
RUN python /krules-mongodb/setup.py install
RUN mv /krules-mongodb/krules_mongodb app/

# add common files here
COPY base_functions.py app/

EOF

rm -rf ./.t_commonlib/

docker push "${DOCKER_REGISTRY}"/${NAME}:"${VERSION}"


#for d in $( find .. -type d -name 'k8s' -not -path ../base/k8s | sed -E 's|/[^/]+$||' | sort -u )
#do
#  pushd "$d" && ${KRULES_ROOT_DIR}/scripts/buildrule.sh && popd
#done