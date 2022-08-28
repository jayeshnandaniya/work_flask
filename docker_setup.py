import subprocess
import time


print('Starting')


subprocess.Popen(['docker-compose', 'up', '-d'], shell=True)


time.sleep(120)


subprocess.Popen(['docker-compose', 'down'], shell=True)


time.sleep(30)


subprocess.Popen(['docker-compose', 'up', '-d', 'db'], shell=True)


time.sleep(120)


subprocess.Popen(['docker-compose', 'run', '--rm', 'flaskapp', '/bin/bash', '-c', "cd /opt/services/flaskapp/src && python -c  'import create_volumes_and_tables'"], shell=True)


time.sleep(60)


subprocess.Popen(['docker-compose', 'down'], shell=True)


print('Done')
