from __future__ import unicode_literals
from ftplib import FTP
import youtube_dl
from os import listdir
import os
class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}

dlFile = open("dlList.txt", "r")
x = dlFile.readlines()
for line in x:
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        if len(line) > 0:
            ydl.download([line])
print("Done downloading, now ftping")
host = '192.168.1.33'
port = 2221
name = 'francis'
password = 'francis'
print("Connecting via ftp")
ftp = FTP()
ftp.connect(host, port)
print("Connection complete, now logging in")
ftp.login(name, password)
print("Login complete")

path = "E:\YoutubeDownloader"
dirs = listdir(path)
for file in dirs:
    if '.mp3' in file:
        ftp.storbinary('STOR '+file, open(file, 'rb'))
print("Ftp done, now closing connection")
ftp.close()
print("Time to clean up the mess")
for file in dirs:
    if '.mp3' in file:
        os.remove(file)
open("dlList.txt","w").close()
