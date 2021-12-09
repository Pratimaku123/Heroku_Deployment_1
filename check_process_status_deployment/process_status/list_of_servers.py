#! /bin/python

import os,sys,getpass
import pandas as pd,numpy as np
USER=getpass.getuser()
REPO_NAME='trade_server_configs'

REPO_PATH='/home/'+USER+'/'+REPO_NAME


def server_list():
    server_name=[]
    for dir,subdir,file in os.walk(REPO_PATH):
        if dir.endswith('.nse.aptportfolio.com'):
            server_name.append(dir.split("/")[-1].split(".")[0])
    server_name=list(set(server_name))
    return server_name

print(server_list())

