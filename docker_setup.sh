#!/bin/bash

echo 'Starting'

docker-compose up -d 
docker-compose down

docker-compose up -d db
docker-compose run --rm flaskapp /bin/bash -c "cd /opt/services/flaskapp/src && python -c  'import create_volumes_and_tables'"
docker-compose down

echo ""
echo "You ready, fam"
