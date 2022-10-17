DICOM Server to Twitter bot
===========================

Clone to /opt/dicom-to-tweet/

`git clone https://github.com/willfurnell/dicom-to-tweet/ /opt/dicom-to-tweet/`

Rename config_sample.py to config.py and enter the Twitter API credentials.

Copy the systemd unit to the appropriate place on your system - `/etc/systemd/system`

Requirements

```
pillow
pynetdicom
pydicom
numpy
tweepy
```

Install with `pip3 install -r requirements.txt` - but probably best to install pillow via your package manager due to dependencies.


```
systemctl enable dicomtweet
systemctl start dicomtweet
```