from Components.ActionMap import ActionMap
from Components.Label import Label
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from Screens.Screen import Screen
from Tools.Directories import fileExists
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, config, ConfigYesNo, ConfigSelection, NoSave

class Bh_Bfull_main(Screen, ConfigListScreen):
    skin = '\n\t<screen position="center,center" size="902,340" title="Mediasat Full Backup">\n\t\t<widget name="config" position="30,10" size="840,60" scrollbarMode="showOnDemand"/>\n\t\t<widget name="lab1" position="30,70" size="840,60" font="Regular;24" valign="center" transparent="1"/>\n\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="200,290" size="140,40" alphatest="on"/>\n\t\t<ePixmap pixmap="skin_default/buttons/green.png" position="550,290" size="140,40" alphatest="on"/>\n\t\t<widget name="key_red" position="200,290" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>\n\t\t<widget name="key_green" position="550,290" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        ConfigListScreen.__init__(self, self.list)
        self['key_red'] = Label(_('Backup'))
        self['key_green'] = Label(_('Cancel'))
        self['lab1'] = Label('')
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'red': self.doBackUp,
         'green': self.close,
         'back': self.close})
        self.updateList()
        self.deviceok = True

    def updateList(self):
        myusb = myusb1 = myhdd = ''
        myoptions = []
        if fileExists('/proc/mounts'):
            f = open('/proc/mounts', 'r')
            for line in f.readlines():
                if line.find('/media/usb') != -1:
                    myusb = '/media/usb/'
                elif line.find('/media/usb1') != -1:
                    myusb1 = '/media/usb1/'
                elif line.find('/hdd') != -1:
                    myhdd = '/media/hdd/'

            f.close()
        if myusb:
            myoptions.append((myusb, myusb))
        if myusb1:
            myoptions.append((myusb1, myusb1))
        if myhdd:
            myoptions.append((myhdd, myhdd))
        self.list = []
        self.myepg_path = NoSave(ConfigSelection(choices=myoptions))
        epg_path = getConfigListEntry(_('Path to store Full Backup'), self.myepg_path)
        if len(myoptions) > 0:
            self.list.append(epg_path)
            self['config'].list = self.list
            self['config'].l.setList(self.list)
        else:
            self['lab1'].setText(_('Sorry no device found to store backup. Please check your media in Mediasat devices panel.'))
            self.deviceok = False

    def doBackUp(self):
        if self.myepg_path.value:
            mytitle = _('Mediasat Full Backup on: ') + self.myepg_path.value
            cmd = '/usr/bin/pme_backup_full.sh ' + self.myepg_path.value
            self.session.open(Console, title=mytitle, cmdlist=[cmd], finishedCallback=self.myEnd)
        else:
            self.session.open(MessageBox, _('Sorry no device found to store backup. Please check your media in Mediasat devices panel.'), MessageBox.TYPE_INFO)

    def myEnd(self):
        self.close()


def main(session, **kwargs):
    session.open(Bh_Bfull_main)


def menu(menuid, **kwargs):
    if menuid == 'mebackup':
        return [(_('MediaSat Full Backup'),
          main,
          'MediaSatFullBackup',
          1)]
    return []


def Plugins(**kwargs):
    return PluginDescriptor(name='MediaSatFullBackup', description=_('Mediasat full image backup'), where=PluginDescriptor.WHERE_MENU, fnc=menu)