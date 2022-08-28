import os
import sys
from inspect import getsourcefile


def get_env_file_path():
    current_path = os.path.abspath(getsourcefile(lambda: 0))
    current_dir = os.path.dirname(current_path)
    grandparent_dir = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))
    
    return os.path.join(grandparent_dir, 'env_file')


def get_env_variables(env_file):
    environ = {}
    with open(env_file, 'r') as ef:
        for line in ef:
            key, value = line.split('=')
            environ[key] = value.rstrip()
            
    return environ


def set_env_variables(vars_dict):
    for key, value in vars_dict.items():
        os.environ[key] = value


def set_project_environment():
    env_file = get_env_file_path()
    vars_dict = get_env_variables(env_file)
    set_env_variables(vars_dict)
