from Components.ActionMap import ActionMap
from Components.Label import Label
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import fileExists
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, config, ConfigYesNo, ConfigSelection, NoSave
from MediaSat.MeUtils import nab_Read_CCCinfoCfg
from os import system, rename as os_rename, remove as os_remove
from enigma import eEPGCache

class Bh_Bepg_main(Screen):
    skin = '\n\t\t<screen position="center,center" size="710,340" title="Mediasat Epg Backup" >\n\t\t\t<widget name="lab1" position="20,20" size="680,64" font="Regular;24" valign="center" transparent="1"/>\n\t\t\t<widget name="lab2" position="20,140" size="300,32" font="Regular;24" valign="center" transparent="1"/>\n\t\t\t<widget name="labstop" position="330,140" size="140,32" font="Regular;24" valign="center"  halign="center" backgroundColor="red"/>\n\t\t\t<widget name="labrun" position="330,140" size="140,32" zPosition="1" font="Regular;24" valign="center"  halign="center" backgroundColor="green"/>\n\t\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="140,290" size="140,40" alphatest="on" />\n\t\t\t<ePixmap pixmap="skin_default/buttons/green.png" position="460,290" size="140,40" alphatest="on" />\n\t\t\t<widget name="key_red" position="140,290" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<widget name="key_green" position="460,290" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t</screen>\n\t\t'

    def __init__(self, session, args = None):
        Screen.__init__(self, session)
        self['lab1'] = Label(_('Epg Backup: not found.'))
        self['lab2'] = Label(_('Automatic Epg Backup:'))
        self['labstop'] = Label(_('Disabled'))
        self['labrun'] = Label(_('Enabled'))
        self['key_red'] = Label(_('Restore'))
        self['key_green'] = Label(_('Setup'))
        self.b_active = False
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'ok': self.restorE,
         'cancel': self.close,
         'red': self.restorE,
         'green': self.setuP}, -1)
        self.onLayoutFinish.append(self.updateT)

    def updateT(self):
        self['labrun'].hide()
        self['labstop'].hide()
        self.b_active = False
        mytext = _('Epg Backup: not found.')
        if fileExists('/etc/bhepgbackup'):
            f = open('/etc/bhepgbackup', 'r')
            line = f.readline()
            line = line.strip()
            self.b_active = True
            f.close()
            myfile = line + 'epg.dat.bak'
            if fileExists(myfile):
                mytext = _('Epg Backup found: ') + myfile
        self['lab1'].setText(mytext)
        if self.b_active == True:
            self['labstop'].hide()
            self['labrun'].show()
        else:
            self['labstop'].show()
            self['labrun'].hide()

    def setuP(self):
        check = False
        if fileExists('/proc/mounts'):
            f = open('/proc/mounts', 'r')
            for line in f.readlines():
                if line.find('/media/cf') != -1:
                    check = True
                elif line.find('/media/usb') != -1:
                    check = True
                elif line.find('/media/card') != -1:
                    check = True
                elif line.find('/hdd') != -1:
                    check = True

            f.close()
        if check == False:
            self.session.open(MessageBox, _('Sorry no device found to store backup.'), MessageBox.TYPE_INFO)
        else:
            self.session.openWithCallback(self.updateT, Bh_Bepg_setuP)

    def restorE(self):
        myepgpath = config.misc.epgcache_filename.value
        if fileExists('/etc/bhepgbackup'):
            f = open('/etc/bhepgbackup', 'r')
            line = f.readline()
            line = line.strip()
            f.close()
            myfile = line + 'epg.dat.bak'
            if fileExists(myfile):
                cmd = 'mv ' + myfile + ' ' + myepgpath
                rc = system(cmd)
                epgcache = eEPGCache.getInstance()
                epgcache.load()
                self.session.open(MessageBox, _('Epg backup successfully restored.'), MessageBox.TYPE_INFO)
                epgcache.save()
            else:
                self.session.open(MessageBox, _('Sorry Epg Backup not found. Please download epg before to restore.'), MessageBox.TYPE_INFO)
        else:
            self.session.open(MessageBox, _('You have to activate Backup before to Restore.'), MessageBox.TYPE_INFO)


class Bh_Bepg_setuP(Screen, ConfigListScreen):
    skin = '\n\t<screen position="center,center" size="902,340" title="Mediasat Devices Mountpoints Setup">\n\t\t<widget name="config" position="30,10" size="840,290" scrollbarMode="showOnDemand"/>\n\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="200,300" size="140,40" alphatest="on"/>\n\t\t<ePixmap pixmap="skin_default/buttons/green.png" position="550,300" size="140,40" alphatest="on"/>\n\t\t<widget name="key_red" position="200,300" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>\n\t\t<widget name="key_green" position="550,300" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        ConfigListScreen.__init__(self, self.list)
        self['key_red'] = Label(_('Save'))
        self['key_green'] = Label(_('Cancel'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'red': self.saveMysets,
         'green': self.close,
         'back': self.close})
        self.updateList()

    def updateList(self):
        mycf = myusb = mysd = myhdd = ''
        myoptions = []
        if fileExists('/proc/mounts'):
            f = open('/proc/mounts', 'r')
            for line in f.readlines():
                if line.find('/media/cf') != -1:
                    mycf = '/media/cf/'
                elif line.find('/media/usb') != -1:
                    myusb = '/media/usb/'
                elif line.find('/media/card') != -1:
                    mysd = '/media/card/'
                elif line.find('/hdd') != -1:
                    myhdd = '/media/hdd/'

            f.close()
        if mycf:
            myoptions.append((mycf, mycf))
        if myusb:
            myoptions.append((myusb, myusb))
        if mysd:
            myoptions.append((mysd, mysd))
        if myhdd:
            myoptions.append((myhdd, myhdd))
        self.list = []
        self.deliteepgenabled = NoSave(ConfigYesNo(default=True))
        self.myepg_path = NoSave(ConfigSelection(choices=myoptions))
        if fileExists('/etc/bhepgbackup'):
            self.deliteepgenabled.value = True
        else:
            self.deliteepgenabled.value = False
        if fileExists('/etc/bhepgbackup'):
            f = open('/etc/bhepgbackup', 'r')
            line = f.readline()
            line = line.strip()
            my_tmp_path = line
            f.close()
            self.myepg_path.value = my_tmp_path
        epg_enabled = getConfigListEntry(_('Enable Automatic Epg Backup'), self.deliteepgenabled)
        self.list.append(epg_enabled)
        epg_path = getConfigListEntry(_('Path to save Backup Epg File'), self.myepg_path)
        self.list.append(epg_path)
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    def saveMysets(self):
        if fileExists('/etc/bhepgbackup'):
            if self.deliteepgenabled.value == False:
                os_remove('/etc/bhepgbackup')
        if self.deliteepgenabled.value == True:
            out = open('/etc/bhepgbackup', 'w')
            out.write(self.myepg_path.value)
            out.close()
        self.close()


def main(session, **kwargs):
    session.open(Bh_Bepg_main)


def menu(menuid, **kwargs):
    if menuid == 'mebackup':
        return [(_('MediaSat Epg Backup'),
          main,
          'MediaSatEpgBackup',
          3)]
    return []


def Plugins(**kwargs):
    return PluginDescriptor(name='MediaSatEpgBackup', description=_('plugin to Backup/Restore Epg'), where=PluginDescriptor.WHERE_MENU, fnc=menu)