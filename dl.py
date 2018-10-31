from __future__ import unicode_literals #TODO find out why this is here. Is it used?
from ftplib import FTP
import os
import sys
import getopt
import urllib.request
import winreg
import threading
import getopt
import configparser

youtube_dl_exe_url = "https://yt-dl.org/latest/youtube-dl.exe"
youtube_dl_exe = 'youtube-dl.exe'

videolist = []
videolistlock = threading.Condition()
mp3list = []
mp3listlock = threading.Condition()
downloadfinished = False
convertingfinished = False

def editConfig(valueDict):
    config = configparser.ConfigParser()
    config.read('config.ini')
    keys = list(valueDict.keys())
    for key in keys:
        config['FTP'][key] = valueDict[key]
    with open('config.ini', 'w+') as configfile:
        config.write(configfile)
        configfile.close

def setUsername(username):
    editConfig({'username': username})

def setPassword(password):
    editConfig({'password': password})

def setPassword(host):
    #TODO check that host is an ip address
    editConfig({'host': host})

def setPassword(port):
    #TODO check that port is a port
    editConfig({'port': port})

def setup():
    directorypath = os.path.dirname(os.path.realpath(__file__))
    addToList = 'addToList.bat'
    if os.path.isfile(youtube_dl_exe):
        print('You already have youtube-dl.exe')
    else:
        print('Downloading youtube-dl.exe...')
        try:
            urllib.request.urlretrieve(youtube_dl_exe_url, youtube_dl_exe)
            print('Download sucessful')
        except:
            print("Can't download youtube-dl.exe file")
    try:
        vidToList = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, 'vidToList')
        winreg.OpenKey(vidToList, 'DefaultIcon')
        shell = winreg.OpenKey(vidToList, 'shell')
        openregistry = winreg.OpenKey(shell, 'open')
        winreg.OpenKey(openregistry, 'command')
        print('Registry keys are already set up')
    except:
        try:
            print('Setting up registry keys...')
            vidToList = winreg.CreateKeyEx(winreg.HKEY_CLASSES_ROOT, 'vidToList', 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(vidToList, '', 0, winreg.REG_SZ, 'URL:vra Protocol')
            winreg.SetValueEx(vidToList, 'URL Protocol', 0, winreg.REG_SZ, '')
            defaulticon = winreg.CreateKeyEx(vidToList, 'Defaulticon', 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(defaulticon, '', 0, winreg.REG_SZ, directorypath + '\\' + addToList)
            shell = winreg.CreateKey(vidToList, 'shell')
            openkey = winreg.CreateKeyEx(shell, 'open', 0, winreg.KEY_ALL_ACCESS)
            command = winreg.CreateKeyEx(openkey, 'command', 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(command, '', 0, winreg.REG_SZ, directorypath + '\\' + addToList + '%1')
            print('Registry keys set up')
        except:
            print('You might have to run it in administrator mode')
    #TODO check if ini file is already configured
    config = configparser.ConfigParser()
    config['FTP'] = {'username': 'francic',
                         'password': 'francis',
                         'host': '192.168.1.33',
                         'port': '2221'}
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
        configfile.close()

class DownloadThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print('Downloading videos...')
        #TODO find out if all these globals are needed
        global vidoelist
        global videolistlock
        global downloadfinished
        downloadfinished = False
        dlFiles = open('dlList.txt', 'r')
        videos = dlFiles.readlines()
        dlFiles.close()
        for video in videos:
            os.system('youtube-dl.exe ' + video)
            dirs = os.listdir()
            for file in dirs:
                if '.mp4' not in file:
                    dirs.remove(file)
                else:
                    with videolistlock:
                        if file not in videolist:
                            videolist.append(file)
                            print(file + ' has been downloaded')
                        videolistlock.notify()
        with videolistlock:
            downloadfinished = True
            videolistlock.notify()
        print('Finished downloading all videos')

class ConverterThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)


    def run(self):
        #TODO figure out if all these globals are needed
        print('Starting to convert')
        global downloadfinished
        global convertingfinished
        global videolist
        global videolistlock
        global mp3listlock
        global mp3list
        convertingfinished = False
        with videolistlock:
            while not downloadfinished:
                while len(videolist) == 0:
                    videolistlock.notify()
                    videolistlock.wait()
                for video in videolist:
                    os.system('ffmpeg.exe -i "' + video + '" "' + video[:-4] +'.mp3"')
                    videolist.remove(video)
                    dirs = os.listdir()
                    for file in dirs:
                        if '.mp3' not in file:
                            dirs.remove(file)
                        else:
                            with mp3listlock:
                                if file not in mp3list:
                                    mp3list.append(file)
                                    print(file + ' has been converted')
                                mp3listlock.notify()
        with mp3listlock:
            convertingfinished = True
            mp3listlock.notify()
        print('Finished converting')
            
class FTPThread(threading.Thread):
    
    def __init__(self, username, password, host, port):
        threading.Thread.__init__(self)
        self.username = username
        self.password = password
        self.host = host
        self.port = port

    def run(self):
        directorypath = os.path.dirname(os.path.realpath(__file__))
        print('Starting ftp')
        ftp = FTP()
        ftp.connect(self.host, self.port)
        print("Connection complete, now logging in")
        ftp.login(self.username, self.password)
        print("Login complete")
        #TODO find out if all these globals are needed
        global convertingfinished
        global mp3listlock
        global mp3list
        with mp3listlock:
            print('Starting ftp')
            while not convertingfinished:
                while len(mp3list) == 0:
                    mp3listlock.notify()
                    print('sleep')
                    mp3listlock.wait()
                for mp3 in mp3list:
                    print('mp3')
                    ftp.storbinary('STOR '+mp3, open(mp3, 'rb'))
                    mp3list.remove(mp3)
                    print('Done ftping ' + mp3)
        print('ftp done, closing connection')
        ftp.close()

def cleanup():
    print('Starting the cleanup process')
    dirs = os.listdir()
    print(dirs)
    for file in dirs:
        if '.mp3' in file or '.mp4' in file:
            os.remove(file)
    open("dlList.txt","w").close()
    print('Done cleaning up')
                    
def main(argv):
    #Default values
    host = '192.168.1.33'
    port = 2221
    username = 'francis'
    password = 'francis'

    #Get values from config file
    #TODO figure out some more efficient method of setting ftp values
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
        ftp = donfig['FTP']
        host = ftp['host']
        port = int(ftp['port'])
        username = ftp['username']
        password = ftp['password']
    #TODO figure out which kind of exception is thrown here and handle it
    except:
        pass
    
    try:
        opts, args = getopt.getopt(argv, 'hu:p:', ['ip=', 'port='])
    except getopt.GetoptError:
        print('Temp error message')
        usage()
        sys.exit()
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt == '-u':
            name = arg
        elif opt == '-p':
            password = arg
        elif opt == '--host':
            host = arg
        elif opt == '--port':
            port = int(arg)
    if args[0] == 'run':
        thread1 = DownloadThread()
        thread2 = ConverterThread()
        thread3 = FTPThread(username, password, host, port)
        thread1.start()
        thread2.start()
        thread3.start()
        thread1.join()
        thread2.join()
        thread3.join()
        cleanup()
    elif args[0] == 'setup':
        setup()
    elif args[0] == 'username':
        try:
            setUsername(args[1])
        except IndexError:
            #TODO better error message
            print('Temp error message')
            usage()
    elif args[0] == 'password':
        try:
            setUsername(args[1])
        except IndexError:
            #TODO better error message
            print('Temp error message')
            usage()
    elif args[0] == 'host':
        try:
            setUsername(args[1])
        except IndexError:
            #TODO better error message
            print('Temp error message')
            usage()
    elif args[0] == 'port':
        try:
            setUsername(args[1])
        except IndexError:
            #TODO better error message
            print('Temp error message')
            usage()
            
    

def usage():
    print('Temp usage message')

if __name__ == "__main__":
   main(sys.argv[1:])
