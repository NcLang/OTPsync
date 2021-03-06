OTPsync
========

_A Python-based project to use One-Time-Pad encryption for untrustworthy Cloud services such as Dropbox._

Applications
------------

One-time pad encryption is only beneficial for encrypting *small* but *often changing* files.
To put it in a nutshell, OTPsync is meant for the synchronization of
- small, often changing files
- that are highly confidential
- via a high-risk communication channel.

The motivation behind OTPsync was to find a viable solution to sync my password manager files, private keys, and bitcoin wallets via untrustworthy channels (such as Dropbox) between my desktop machine at home, my laptop, and my computer at work.


Installation
------------

OTPsync was successfully tested on Linux (Arch & Ubuntu) and OSX (Yosemite). 
Compatibility with Windows may require minor tweaks of the code.

The following conditions must be met:
- OTPsync relies on the established script ```onetime``` for encryption and pad management. 
  You can download it at http://www.red-bean.com/onetime/. It is a single Python 2.7 script.
  For some Linux distributions, there are even packages in the official repositories, e.g. for Ubuntu
  ```sudo apt-get install onetime```
- ```onetime``` requires python 2.7
- ```otpsync``` requires python 3.4

During setup of a OTPsync directory, you will be asked the path to ```onetime```.
In the following it is assumed that ```onetime``` is available via ```/usr/bin/onetime```.


Setting up OTPsync
------------------

To create the required file structures, change to the directory which should be synced and call
```bash
otpsync init
```
You will be asked to specify several parameters.

During the setup procedure, the script copies itself into the cloud repository; so all the other clients get a copy of the script automatically.

Finally, start a full synchronization via
```bash
otpsync sync
```

As long as files only changed (no deleted or newly created files), a quick sync can be invoced just by calling
```bash
otpsync
```
This will update all existing remote and local files depending on their modification dates without asking any questions. Newly created and/or deleted files will be ignored.

Once set up, the workflow is straightforward: 
Say, your password manager file changed on your computer at home.
Call ```otpsync``` first in the directory with the changed file and then at work (or on your notebook) again.
This will consume some KB of the "randomness" in your pads. 
However, given a 1GB pad and daily transfers of (say) 100KB of data (which is sufficient for password synchronization) requires a new pad after about 30 years. So the price you pay is negligible compared to the outstanding level of security you get.

Creating One-Time Pads
----------------------

To create a 10MB pad from /dev/random, call
```bash
dd if=/dev/random of=/path/to/new.pad bs=1024 count=10024
```
