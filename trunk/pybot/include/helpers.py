# -*- coding: utf-8 -*-

# $Id$

from os.path import abspath, dirname, isabs, join, devnull
from subprocess import check_output, CalledProcessError, STDOUT
import sys

def get_svn_version():

    script_dir = abspath(dirname(sys.argv[0]))
    try:
        f=open(devnull, 'w')
        version = check_output(['svnversion',script_dir], stderr=f)
        f.close()
    except CalledProcessError:
        version = ''
    except OSError:
        version = ''
    
    return 'svn('+version.strip()+')'
        
def get_version():
    return get_svn_version()
