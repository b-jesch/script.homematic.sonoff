#!/usr/bin/python

import sys
import socket
import io
import os
from resources.lib.tools import *
from resources.lib.sonoff import Sonoff
from resources.lib.scanner import Scanner

iconpath = os.path.join(PATH, 'resources', 'media')
scannerfile = os.path.join(PROFILE, 'scanner.json')

writeLog('Addon started')

devices = list()
for i in xrange(1, 9):
    if getAddonSetting('%s_enabled' % (i), sType=BOOL):
        for j in xrange(0, getAddonSetting('%s_channels' % (i), sType=NUM) + 1):
            device_properties = {'switchable': getAddonSetting('%s_switchable' % (i), sType=BOOL),
                                      'ip': getAddonSetting('%s_ip' % (i)),
                                      'channel': j,
                                      'multichannel': True if getAddonSetting('%s_channels' % (i), sType=NUM) > 0 else False,
                                      'name': getAddonSetting('%s_name_%s' % (i, j))}
            devices.append(device_properties)

if __name__ == '__main__':
    try:
        if sys.argv[1].upper() == 'SCAN':
            writeLog('Initiate Network Scan...')

            if getAddonSetting('autodetect', sType=BOOL):
                host = None
                interfaces = socket.gethostbyname_ex(socket.gethostname())[-1]
                for interface in interfaces:
                    if interface in ('127.0.0.1', 'localhost'): continue
                    host = interface
                    break

                if host is None:
                    dialogOK(LS(30000), LS(30026))
                    exit()

                ip_subset = host.split('.')
                ip_subset.pop()
                setAddonSetting('netmask', '{}.0'.format('.'.join(ip_subset)))
            else:
                ip_subset = getAddonSetting('netmask').split('.')
                if getAddonSetting('netmask') == '0.0.0.0' or len(ip_subset) != 4:
                    dialogOK(LS(30000), LS(30025))
                    exit()
                else:
                    ip_subset.pop()

            mask = '.'.join(ip_subset)
            start = getAddonSetting('range_start', sType=NUM) - 1
            stop = getAddonSetting('range_stop', sType=NUM)
            ports = ' '.join(getAddonSetting('portlist').replace(',', ' ').split()).split()

            sd = Sonoff()
            scanner = Scanner()

            scanner.scan(mask, start, stop, ports)
            if len(scanner.net_devices) > 0:
                for net_device in scanner.net_devices:
                    props = sd.send(scanner.net_devices[net_device]['ip'], sd.NAME[0])
                    writeLog('Device Properties: {}'.format(str(props)))
                    if props != "UNDEFINED":
                        scanner.net_devices[net_device].update({'name': props.get('DeviceName', 'unknown')})
                        scanner.net_devices[net_device].update({'channels': props.get('FriendlyName', [])})

                with io.open(scannerfile, 'w', encoding='utf-8') as sf:
                    content = json.dumps(scanner.net_devices, ensure_ascii=False, indent=4)
                    sf.write(unicode(content))

                notify(LS(30000), LS(30027))

        elif sys.argv[1].upper() == 'APPLY':
            if os.path.isfile(scannerfile):
                with io.open(scannerfile, 'r', encoding='utf-8') as sf:
                    net_devices = json.load(sf)
                    writeLog('Load {} entries from net device list'.format(len(net_devices)))
                menu = list()

                for net_device in net_devices:

                    if 'name' in net_devices[net_device]:
                        icon = os.path.join(iconpath, 'network_td.png')
                        label = '{} ({})'.format(net_device.encode('utf-8'),
                                                 net_devices[net_device].get('name').encode('utf-8'))
                    else:
                        icon = os.path.join(iconpath, 'network.png')
                        label = net_device.encode('utf-8')

                    liz = xbmcgui.ListItem(label=label, label2=net_devices[net_device]['ip'])
                    liz.setArt({'icon': icon})
                    liz.setProperty('channels', ', '.join(net_devices[net_device].get('channels', [LS(30017)])))
                    menu.append(liz)

                entry = xbmcgui.Dialog().select(LS(30037), menu, useDetails=True)
                if entry < 0:
                    exit()
                setAddonSetting('{}_ip'.format(sys.argv[2]), menu[entry].getLabel2())
                setAddonSetting('{}_channels'.format(sys.argv[2]),
                                len(menu[entry].getProperty('channels').split(',')) - 1)

                i = 0
                for channel in menu[entry].getProperty('channels').split(','):
                    setAddonSetting('{}_name_{}'.format(sys.argv[2], i), channel)
                    i += 1
            else:
                writeLog('No device list found...')
                dialogOK(LS(30000), LS(30029))

    except IndexError:
        _devlist = []
        with busy_dialog():
            for device in devices:
                sd = Sonoff()
                if device['multichannel']:
                    device.update({'status': sd.send(device['ip'], sd.STATUS[device['channel']], channel=device['channel'] + 1, timeout=5)})
                else:
                    device.update({'status': sd.send(device['ip'], sd.STATUS[device['channel']], timeout=5)})

                if device['status'] == 'ON':
                    L2 = LS(30021) if device['switchable'] else LS(30024)
                    icon = os.path.join(iconpath, 'sonoff_on.png')
                elif device['status'] == 'OFF':
                    L2 = LS(30020) if device['switchable'] else LS(30024)
                    icon = os.path.join(iconpath, 'sonoff_off.png')
                elif device['status'] == 'UNDEFINED':
                    L2 = LS(30022)
                    icon = os.path.join(iconpath, 'sonoff_undef.png')
                    device.update({'switchable': False})
                else:
                    L2 = LS(30023)
                    icon = os.path.join(iconpath, 'sonoff_undef.png')
                    device.update({'switchable': False})

                liz = xbmcgui.ListItem(label=device['name'], label2=L2)
                liz.setArt({'icon': icon})
                liz.setProperty('name', device['name'])
                liz.setProperty('ip', device['ip'])
                liz.setProperty('channel', str(device['channel']))
                liz.setProperty('switchable', str(device['switchable']))
                _devlist.append(liz)

        if len(_devlist) > 0:
            dialog = xbmcgui.Dialog()
            _idx = dialog.select(LS(30000), _devlist, useDetails=True)
            if _idx > -1:
                if strToBool(_devlist[_idx].getProperty('switchable')):
                    res = sd.send(_devlist[_idx].getProperty('ip'), sd.TOGGLE[int(_devlist[_idx].getProperty('channel'))])
                    writeLog('{} ({}) switched to {}'.format(_devlist[_idx].getProperty('name'), _devlist[_idx].getProperty('ip'), res))
                else:
                    writeLog('{} ({}) is not switchable'.format(_devlist[_idx].getProperty('name'), _devlist[_idx].getProperty('ip')))
                    notify(LS(30000), LS(30014) % (_devlist[_idx].getProperty('name').decode('utf-8')), icon=xbmcgui.NOTIFICATION_WARNING)
        else:
            writeLog('no switchable devices found')
            notify(LS(30000), LS(30015), icon=xbmcgui.NOTIFICATION_WARNING)