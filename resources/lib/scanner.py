from tools import *
import socket


class Scanner(object):

    def __init__(self):
        self.net_devices = dict()

    def connect(self, ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, int(port)))
        sock.close()
        return result == False

    def scan(self, segment, start, stop, ports):
        pb = xbmcgui.DialogProgress()
        steps = 100.0 / (stop - start)
        pb.create(LS(30000), LS(30040))
        xbmc.sleep(2000)

        for port in ports:

            progress = 0
            msg_1 = LS(30041).format(segment, start + 1, stop, port).encode('utf-8')
            msg_2 = ''

            writeLog("Scanning Port {} from {}.{} to {}.{}".format(port, segment, start + 1, segment, stop))
            for i in range(start, stop):
                res = self.connect("{}.{}".format(segment, i), port)
                progress += steps
                if res:
                    _dev = socket.gethostbyaddr('{}.{}'.format(segment, i))[0]
                    msg_2 = LS(30042).format(segment, i, port, _dev).encode('utf-8')
                    writeLog("Device found at: {}.{}:{} {}".format(segment, i, port, _dev))
                    self.net_devices.update({_dev: {'ip': '{}.{}'.format(segment, i)}})
                pb.update(int(progress), '{}{}'.format(msg_1, msg_2))
                if pb.iscanceled():
                    pb.close()
                    writeLog('Scan aborted')
                    dialogOK(LS(30000), LS(30028))
                    self.net_devices.clear()
                    return
        pb.close()
        writeLog('Scan successful finished')

