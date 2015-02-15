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

OTPsync relies on the established script *onetime* for encryption and pad management. 

You can download it at http://www.red-bean.com/onetime/. It is a single Python 2.7 script.

For some Linux distributions, there are even packages in the official repositories, e.g. for Ubuntu
```bash
sudo apt-get install onetime
```

During setup of a OTPsync directory, you will be asked the path to *onetime*.

Setting up OTPsync
------------------

To create the required file structures, change to the directory which should be synced and call
```bash
otpsync init
```
You will be asked to specify several parameters.

Finally, start a full synchronization via
```bash
otpsync sync
```

Creating One-Time Pads
----------------------

To create a 10MB pad from /dev/random, call
```bash
dd if=/dev/random of=/path/to/new.pad bs=1024 count=10024
```
