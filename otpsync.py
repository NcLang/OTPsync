#!/usr/bin/env python3.4
##
## ONE-TIME SYNC
## ==============
## (A one-time pad encryption for cloud services)
##
## By Nicolai Lang
## Run as >> python3 ./otpsync.py

## Modules
import sys
import os.path
import os
import imp
import re
from subprocess import call
import datetime
from os.path import expanduser
import hashlib
import filecmp
import shutil
import time


#-------------------------
# Parameters
#-------------------------

DT = 60 # time difference for newer files (sec)
sys.dont_write_bytecode = True
    
#-------------------------
# Functions for printing
#-------------------------

## Colors
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = "\033[1m"

def out_done():
    print(" [" + bcolors.OKGREEN + "done" + bcolors.ENDC + "]",end="",flush=True)

def out_green(x):
    print("\n--> " + bcolors.OKGREEN + x + bcolors.ENDC, end="",flush=True)

def out_blue(x):
    print("\n--> " + bcolors.OKBLUE + x + bcolors.ENDC, end="",flush=True)

def out_head(x):
    print("\n--> " + bcolors.HEADER + x + bcolors.ENDC, end="",flush=True)

def out_text(x):
    print("\n--> " + x, end="",flush=True)

def out_line():
    print("\n===================================================", end="",flush=True)


#-------------------------
# Miscellaneous functions
#-------------------------

## Latest local modification
def all_files_of(b='.'):
    result = []
    for d in os.listdir(b):
        bd = os.path.join(b, d)
        result.append(bd)
    return result

## Clear folder
def clear_folder(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        if os.path.isfile(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
            
## Create file tree with modification times
def file_structure(folder):
    a_files = []
    a_dirs = []
    regex=re.compile("^\./\.otpsync.*$")
    for path, dirs, files in os.walk(folder):
        if re.match(regex,path) == None:
            a_dirs.append([os.path.relpath(path+"/",folder),mod_time(path)])
            for file in files:
                a_files.append([os.path.join(os.path.relpath(path,folder),file),mod_time(os.path.join(path,file))])
    return (a_dirs,a_files)

## Modification times
def mod_time(filename):
    return os.path.getmtime(filename)
    
## Print help
def print_help():
    out_line()
    out_head("++++++++++++++++ OTPsync v0.1 ++++++++++++++++")
    out_head("Help / List of options")
    out_line()
    out_blue("Call otpsync <option> with the following options:")
    out_text("no argument : Start basic synchronization (update changed files without asking).")
    out_text("help, h, -h : Print this info text.")
    out_text("sync, s, -s : Start full synchronization (add/delete files).")
    out_text("init, i, -i : Make the current directory a otpsync directory.")
    out_text("push, p, -p : Push local data in cloud (overwrites remote files).")
    out_text("get, g, -g  : Get remote data (overwrites local files).")
    out_text("copy, c, -c : Copy this script into the cloud.")
    out_text("otp, o, -o  : Generate a one-time pad via /dev/random for this client ID.")
    out_line()
    
## Print info
def print_info():
    out_line()
    out_head("++++++++++++++++ OTPsync v0.1 ++++++++++++++++")
    out_head("One-Time Pad Encryption for High-Risk Channels")
    out_line()
    out_text("For updates of this script visit:")
    out_text("www.nicolailang.de/Projects/OTPsync")
    out_text("This script relies on otpsync for OTP encryption.")
    out_text("For updates of otpsync visit:")
    out_text("www.red-bean.com/onetime/")
    out_text("Here some reminders:")
    out_blue("+ Keep your one time pads safe !!!")
    out_blue("+ Do NOT use pseudo RNGs for pad creation !!!")
    out_blue("+ Do NEVER reuse one (!!!) time pads !!!")
    out_blue("+ OTPsync is NO REPLACEMENT for ")
    out_blue("  strong passwords and local encryption !!!")
    out_line()
    
## Ask user for input with default value
def def_input(description,default):
    data = input("\n==> "+description+" ["+default+"]: ")
    if data == '':
        data = default
    return(str(data))

## Create directory if it does not exist
def create_dir(pth):
    if not os.path.exists(expanduser(pth)):
        os.makedirs(expanduser(pth))
        
## Differences of nested lists
def diff(a, b):
    bnames = [item[0] for item in b]
    return [aa[0] for aa in a if aa[0] not in bnames]

## Intersection of nested lists
def intsct(a, b):
    bnames = [item[0] for item in b]
    return [aa[0] for aa in a if aa[0] in bnames]

## Get modification time by path
def get_time(path,lst):
    return int([aa[1] for aa in lst if (aa[0] == path)][0])


#*************************************************
# OTPsync Class
#*************************************************

class otpsync:

    def __init__(self):
        self.config = {}
        self.rconfig = {}
        self.script_path=os.path.realpath(__file__)

        
    ## Check whether config file is present
    def under_control(self,pth):
        ok = True
        if not os.path.exists(pth+'.otpsync'):
            ok = False
        else:
            if not os.path.exists(pth+'.otpsync/otpsync.cfg'):
                ok = False
        return(ok)

    
    ## Load configuration file
    def load_config(self,pth):
        regex=re.compile("^([a-zA-Z]+) = (.+)$")
        with open(pth+'.otpsync/otpsync.cfg', "r") as cfg:
            for line in cfg:
                result = re.match(regex,line)
                self.config[result.group(1)] = result.group(2)
        out_text("Found the following OTPsync parameters:")
        fmt_data = '{0:7} = {1:20}'
        for key, parameter in self.config.items():
            out_green(fmt_data.format(key,parameter))

            
    ## Create OTPsync structure
    def create_config(self,pth):
        ## Create directories & files
        create_dir(pth+'.otpsync')
        ## Write configuration
        with open('.otpsync/otpsync.cfg', "w+") as output:

            ## Path to OTPs
            data1 = def_input('Path to OTPs','.otpsync/pads/')    
            output.write('PADS'+' = '+expanduser(data1)+'\n')

            ## Path to temporary files
            data2 = def_input('Path to temporary files','.otpsync/tmp/')    
            output.write('TMP'+' = '+expanduser(data2)+'\n')

            ## Path to backups
            data6 = def_input('Path to backups','.otpsync/backup/')
            output.write('BACKUP'+' = '+expanduser(data6)+'\n')

            ## Path to cloud directory
            data3 = def_input('Path to cloud directory','~/Dropbox/otpsync/')
            output.write('CLOUD'+' = '+expanduser(data3)+'\n')

            ## Path to onetime
            data7 = def_input('Path to onetime','/usr/bin/onetime')
            output.write('ONETIME'+' = '+expanduser(data7)+'\n')

            ## ID of this instance
            data4 = def_input('OTPsync ID','desktop')
            output.write('ID'+' = '+data4+'\n')

            ## ID of OTPsync group
            data5 = def_input('OTPsync group','mysync')
            output.write('GROUP'+' = '+data5+'\n')

            ## Config directory for onetime
            output.write('CONF'+' = '+'.otpsync/onetime'+'\n')
            
        out_text("Writing data to file ...")
        out_text("Creating directories ...")
        ## OTPs
        create_dir(data1)
        ## Temporary files    
        create_dir(data2)
        ## Backups
        create_dir(data6)
        ## Cloud
        create_dir(data3)
        create_dir(data3+data5)
        ## Copy otpsync to remote directory
        if not os.path.exists(expanduser(data3+data5)):
            out_text("Copying otpsync.py to remote directory ...")
            shutil.copy2(self.script_path,expanduser(data3+data5))
        

    ## Get remote archive (copy, decrypt, extract)
    def get_remote(self):
        remote_tar_gz_otp = self.config['CLOUD']+self.config['GROUP']+'/safe.tar.gz.otp'
        local_tar_gz_otp = './.otpsync/safe.tar.gz.otp'

        ## Check whether local files need updating
        do = True
        done = False
        if os.path.exists(remote_tar_gz_otp) and os.path.exists(local_tar_gz_otp):
            if filecmp.cmp(remote_tar_gz_otp,local_tar_gz_otp):
                do = False
                done = True

        ## Get remote config
        out_text("Loading remote config ...")
        self.get_rconfig()

        if do:
            ## Copy remote files
            out_green("Copying remote files ...")
            call(["cp",remote_tar_gz_otp,local_tar_gz_otp])
            out_done()

            ## Decrypt remote files
            out_green("Decrypting remote files ...")
            call(["python2.7",self.config['ONETIME'],"-d","-p",self.find_pad(self.rconfig['ID']),
                  "-C",self.config['CONF'],"-o","./.otpsync/safe.tar.gz",local_tar_gz_otp])
            out_done()

            ## Extract remote files
            out_green("Extracting remote files ...\n")
            clear_folder(self.config['TMP'])
            call(["tar","vxfz","./.otpsync/safe.tar.gz","-C",self.config['TMP']])
            out_done()
            done = True

        return(done)


    ## Put remote archive (compress, encrypt, copy)
    def put_remote(self):
        remote_tar_gz_otp = self.config['CLOUD']+self.config['GROUP']+'/safe.tar.gz.otp'
        local_tar_gz_otp = './.otpsync/safe.tar.gz.otp'

        ## Compress local files
        out_green("Compressing local files ...\n")
        call(["tar","vcfz","./.otpsync/safe.tar.gz","-C",self.config['TMP'],"."])
        out_done()
        ## Encrypt local files
        out_green("Encrypting local files ...")
        call(["python2.7",self.config['ONETIME'],"-e","-C",self.config['CONF'],
              "-p",self.find_pad(self.config['ID']),"-o",local_tar_gz_otp,"./.otpsync/safe.tar.gz"])
        out_done()
        ## Copy local files
        out_green("Copying local files ...")
        call(["cp",local_tar_gz_otp,remote_tar_gz_otp])
        out_done()
        ## Update remote config
        out_green("Updating remote config ...")
        self.set_remoteid(self.config['ID'])
        self.set_remotetime(time.time())
        self.set_rconfig()
        out_done()

        
    ## Find correct pad (use first find if there are multiple pads for one user)
    def find_pad(self,ID):
        regex = re.compile("^.*/"+ID+"_[0-9]{2}-[0-9]{2}-[0-9]{4}_[0-9]{2}-[0-9]{2}-[0-9]{2}\.pad$")
        allpads = all_files_of(self.config['PADS'])
        pads = list(filter(regex.match,allpads))
        
        if len(pads)>0:
            pad = pads[0]
        else:
            out_text("No pad available! Exiting...")
            exit(1)
        return(pad)


    ## Generate pad from /dev/random
    def generate_pad(self):
        size = float(def_input('Size of pad in MB','10'))
        pad_name=self.config['ID']+"_"+datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        out_text("Generating pad '"+pad_name+"'")
        out_text("This may take a while ...")
        call(["dd","if=/dev/random","of="+self.config['PADS']+pad_name,"bs=1000",
              "count="+"{:.0f}".format(1000*size)])
        out_done()

             
    ## Get remote config
    def get_rconfig(self):
        remote_id_file = self.config['CLOUD']+self.config['GROUP']+'/safe.info'
        if os.path.exists(remote_id_file):
            regex=re.compile("^([a-zA-Z]+) = (.+)$")
            with open(remote_id_file, "r") as cfg:
                for line in cfg:
                    result = re.match(regex,line)
                    self.rconfig[result.group(1)] = result.group(2)
            out_text("Found the following remote parameters:")
            fmt_data = '{0:7} = {1:20}'
            for key,parameter in self.rconfig.items():
                out_green(fmt_data.format(key,parameter))
            return(True)
        else:
            return(False)

        
    ## Write remote config
    def set_rconfig(self):
        remote_id_file = self.config['CLOUD']+self.config['GROUP']+'/safe.info'
        with open(remote_id_file, "w+") as output:
            for key, data in self.rconfig.items():
             output.write(key+' = '+str(data)+'\n')

             
    ## Set ID in the cloud
    def set_remoteid(self,ID):
        self.rconfig['ID'] = ID

        
    ## Set timestamp in the cloud
    def set_remotetime(self,T):
        self.rconfig['TIME'] = T

        
    ## Sync
    def sync(self,ask):

        if ask:
            out_text("Starting full synchronization ...")
        else:
            out_text("Starting quick synchronization ...")
            
        updated = False
        
        ## Get remote and local file tree
        local_dirs, local_files = file_structure("./")
        remote_dirs, remote_files = file_structure(self.config['TMP'])

        ## Files to be updated
        update_paths = intsct(local_files,remote_files)

        
        for pth in update_paths:
            ## Local newer than remote
            if get_time(pth,local_files) > get_time(pth,remote_files)+DT:
                shutil.copy2(pth,self.config['TMP']+pth)
                out_head("Updating remote file: "+pth)
                updated = True
            ## Remote newer than local
            elif DT+get_time(pth,local_files) < get_time(pth,remote_files):
                shutil.copy2(self.config['TMP']+pth,pth)
                out_head("Updating local file: "+pth)

                
        ## Consider new/deleted files & folders only if ask=True
        if ask:
                
            ## Find differences and ask user what to do
            ask_files_lr = diff(local_files,remote_files)
            ask_files_rl = diff(remote_files,local_files)

            ## Ask user about "new" files in local directory
            for pth in ask_files_lr:
                out_blue("LOCAL file: "+pth)
                askagain = True
                while askagain:
                    ask = def_input("Local (d)elete / Remote (c)reate / (i)gnore ?","i")
                    if ask == 'c':
                        if not os.path.exists(os.path.dirname(self.config['TMP']+pth)):
                            os.makedirs(os.path.dirname(self.config['TMP']+pth))
                        shutil.copy2(pth,self.config['TMP']+pth)
                        askagain = False
                        updated = True
                    elif ask == 'd':
                        shutil.move(pth,self.config['BACKUP']+pth)
                        askagain = False
                    elif ask == 'i':
                        askagain = False

                        
            ## Ask user about "new" files in remote directory
            for pth in ask_files_rl:
                out_blue("REMOTE file: "+pth)
                askagain = True
                while askagain:
                    ask = def_input("Local (c)reate / Remote (d)elete / (i)gnore ?","i")
                    if ask == 'c':
                        if not os.path.exists(os.path.dirname(pth)):
                            os.makedirs(os.path.dirname(pth))
                        shutil.copy2(self.config['TMP']+pth,pth)
                        askagain = False
                    elif ask == 'd':
                        shutil.move(self.config['TMP']+pth,self.config['BACKUP']+pth)
                        askagain = False
                        updated = True
                    elif ask == 'i':
                        askagain = False

                        
            ## Get remote and local file tree again (files have been added/deleted)
            local_dirs, local_files = file_structure("./")
            remote_dirs, remote_files = file_structure(self.config['TMP'])
            ## Find differences and ask user what to do
            ask_dirs_rl = diff(remote_dirs,local_dirs)

            
            while len(ask_dirs_rl)> 0:
                pth = ask_dirs_rl[0]
                ## Ask user about "new" directories in remote directory
                out_blue("REMOTE directory: "+pth)
                askagain = True
                while askagain:
                    ask = def_input("Local (c)reate / Remote (d)elete / (i)gnore ?","i")
                    if ask == 'c':
                        if not os.path.exists(os.path.dirname(pth)):
                            os.makedirs(os.path.dirname(pth))
                        askagain = False
                    elif ask == 'd':
                        shutil.rmtree(self.config['TMP']+pth)
                        askagain = False
                        updated = True                
                    elif ask == 'i':
                        askagain = False
                
                ## Get remote and local file tree again (directories have been added/deleted)
                local_dirs, local_files = file_structure("./")
                remote_dirs, remote_files = file_structure(self.config['TMP'])
                ## Find differences and ask user what to do
                ask_dirs_rl = diff(remote_dirs,local_dirs)

                
            ## Get remote and local file tree again (files have been added/deleted)
            local_dirs, local_files = file_structure("./")
            remote_dirs, remote_files = file_structure(self.config['TMP'])
            ## Find differences and ask user what to do
            ask_dirs_lr = diff(local_dirs,remote_dirs)

            
            while len(ask_dirs_lr)> 0:
                pth = ask_dirs_lr[0]
                ## Ask user about "new" directories in local directory
                out_blue("LOCAL directory: "+pth)
                askagain = True
                while askagain:
                    ask = def_input("Remote (c)reate / Local (d)elete / (i)gnore ?","i")
                    if ask == 'c':
                        if not os.path.exists(os.path.dirname(self.config['TMP']+pth)):
                            os.makedirs(os.path.dirname(self.config['TMP']+pth))
                        askagain = False
                        updated = True                
                    elif ask == 'd':
                        shutil.rmtree(pth)
                        askagain = False
                    elif ask == 'i':
                        askagain = False
                        
                ## Get remote and local file tree again (directories have been added/deleted)
                local_dirs, local_files = file_structure("./")
                remote_dirs, remote_files = file_structure(self.config['TMP'])
                ## Find differences and ask user what to do
                ask_dirs_lr = diff(local_dirs,remote_dirs)

        return updated

    ## Copy otpsync to remote directory
    def copy_script(self):
        remote_script = self.config['CLOUD']+self.config['GROUP']+'/otpsync.py'
        if not os.path.exists(expanduser(remote_script)):
            out_text("Copying otpsync.py to remote directory ...")
        else:
            out_text("Replacing otpsync.py in remote directory ...")
        shutil.copy2(self.script_path,expanduser(remote_script))
    
                
###################### MAIN ######################

# No parameter
if len(sys.argv) == 1:
    
    ## Check whether local directory is under otpsync control:
    otps = otpsync()
    if otps.under_control("./"):
        print_info()
        otps.load_config("./")
        otps.get_remote()
        out_line()
        synced = otps.sync(False) # Noask
        if synced:
            otps.put_remote()
        out_line()
        out_text("Finished. Have a nice day ...")
        out_line()
        exit(0)
    else:
        print(bcolors.WARNING + "This is not an active OTPsync directory!" + bcolors.ENDC)
        exit(1)

## Single parameter
elif len(sys.argv) == 2:

    ## Print help
    if sys.argv[1] in ['help','-h','h']:
        print_help();
        exit(0)

    ## Copy otpsync.py to remote destination
    if sys.argv[1] in ['copy','-c','c']:
        otps = otpsync()
        if otps.under_control("./"):
            print_info()
            otps.load_config("./")
            out_line()
            otps.copy_script()
            out_line()
            exit(0)
        else:
            print(bcolors.WARNING + "This is not an active OTPsync directory!" + bcolors.ENDC)
            exit(1)

    ## Create OTP from /dev/random for this ID
    if sys.argv[1] in ['otp','-o','o']:
        otps = otpsync()
        if otps.under_control("./"):
            print_info()
            otps.load_config("./")
            out_line()
            otps.generate_pad()
            out_line()
            exit(0)
        else:
            print(bcolors.WARNING + "This is not an active OTPsync directory!" + bcolors.ENDC)
            exit(1)
            
    ## Create OTPsync structure
    if sys.argv[1] in ['init','-i','i']:
        otps = otpsync()
        if not otps.under_control("./"):
            print_info()
            otps.create_config("./")
            exit(0)
        else:
            print(bcolors.WARNING + "This is already an active OTPsync directory!" + bcolors.ENDC)
            exit(1)

    ## Push local data in cloud (overwrites remote files)
    if sys.argv[1] in ['push','-p','p']:
        otps = otpsync()
        if otps.under_control("./"):
            print_info()
            otps.load_config("./")
            while True:
                uin = def_input("Overwrite remote files? (yes|no)","no")
                if uin == 'yes': 
                    otps.put_remote()
                    exit(0)
                elif uin == 'no':
                    exit(0)
        else:
            print(bcolors.WARNING + "This is not an active OTPsync directory!" + bcolors.ENDC)
            exit(1)

    ## Get remote data (overwrites local files)
    if sys.argv[1] in ['get','-g','g']:
        otps = otpsync()
        if otps.under_control("./"):
            print_info()
            otps.load_config("./")
            while True:
                uin = def_input("Overwrite local files? (yes|no)","no")
                if uin == 'yes': 
                    otps.get_remote()
                    exit(0)
                elif uin == 'no':
                    exit(0)
        else:
            print(bcolors.WARNING + "This is not an active OTPsync directory!" + bcolors.ENDC)
            exit(1)
            
    ## Sync directory
    if sys.argv[1] in ['sync','-s','s']:
        ## Check whether local directory is under otpsync control:
        otps = otpsync()
        if otps.under_control("./"):
            print_info()
            otps.load_config("./")
            otps.get_remote()
            out_line()
            synced = otps.sync(True) # Ask
            if synced:
                otps.put_remote()
            out_line()
            out_text("Finished. Have a nice day ...")
            out_line()
            exit(0)
        else:
            print(bcolors.WARNING + "This is not an active OTPsync directory!" + bcolors.ENDC)
            print_help();
            exit(1)

    else:
        print_help();
        exit(0)
            
## Double parameter
elif len(sys.argv) == 3:
    print(bcolors.WARNING + "Wrong number of arguments!" + bcolors.ENDC)
    print_help();
    exit(1)

## No valid call
else:
    print(bcolors.WARNING + "Wrong number of arguments!" + bcolors.ENDC)
    print_help();
    exit(1)

    
###################### MAIN ######################

