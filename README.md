OTPsync
========

_A Python-based project to use One-Time-Pad encryption for untrustworthy Cloud services such as Dropbox._


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
