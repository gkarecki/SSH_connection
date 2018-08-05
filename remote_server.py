import paramiko
import json
from easygui import passwordbox, msgbox
import os
from datetime import datetime

from paramiko import SSHException


def connect(server_address, port, user, password):
    print("User: {}".format(user))
    print("Connecting: {}".format(server_address))
    print("Port: {}".format(port))

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server_address, port, user, password)
        msgbox("Connected to {}, user: {}".format(server_address, user))
        print()
        return ssh
    except paramiko.ssh_exception.AuthenticationException:
        exit("Wrong password! Try again...")


def loadConfig():
    with open("config.json") as json_data:
        data = json.load(json_data)
    return data["server_address"], data["port"], data["username"], \
           passwordbox("password: "), data["local_folder"], \
           data["remote_folder"], data["mode"], data["ignore"]


def overwrite():
    for root, dirs, files in os.walk(local_folder):
        for fileName in files:
            if ignoreFileType(fileName):
                sftp.put(local_folder + fileName, fileName)
                print(fileName + " copied to remote folder.")
    ssh.close()

def add_non_existing():
    for root, dirs, files in os.walk(local_folder):
        for fileName in files:
            if ignoreFileType(fileName):
                try:
                    sftp.stat(fileName)
                except IOError:
                    sftp.put(local_folder + fileName, fileName)
                    print(fileName+ " copied to remote folder.")
    ssh.close()

def update():
    for root, dirs, files in os.walk(local_folder):
        for fileName in files:
            if ignoreFileType(fileName):
                try:
                    sftp.stat(fileName)
                    date1 = datetime.fromtimestamp(os.path.getmtime(local_folder + fileName))
                    date2 = datetime.fromtimestamp(sftp.stat(fileName).st_mtime)

                    if date1 > date2:
                        sftp.put(local_folder + fileName, fileName)
                        print(fileName+ " copied to remote folder.")
                except IOError:
                    pass
    ssh.close()


def ignoreFileType(fileType):
    x = fileType.split(".")
    flag = True
    for y in ignore:
        if x[len(x)-1] == y:
            flag = False
            break
    if flag:
        return True
    return False


host, port, user, password, local_folder, remote_folder, mode, ignore = loadConfig()

try:
    ssh = connect(host, port, user, password)
except SSHException:
    exit("CANCELED")

sftp = ssh.open_sftp()
sftp.chdir(remote_folder)

print("Choosed mode: {}".format(mode))

if mode == "overwrite":
    overwrite()
elif mode == "update":
    update()
elif mode == "add_non_existing":
    add_non_existing()
else:
    ssh.close()
    exit("WRONG MODE!")
