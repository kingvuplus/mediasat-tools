# -*- coding: utf-8 -*-
#Coders by Nikolasi for INDB 9
from Components.VariableText import VariableText
from enigma import eLabel, eEPGCache
from Renderer import Renderer
from time import localtime

class NextEvent2(Renderer, VariableText):
	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self)
		self.epgcache = eEPGCache.getInstance()

	GUI_WIDGET = eLabel
	def changed(self, what):
		event = self.source.event
		if event is None:
			self.text = "No EPG data available"        # string is " " empty (show nothing)... you can edit like: (self.text = "No EPG Data" ) and this will show when epg/event is empty
			return None
		service = self.source.service
		text = "Next: "
		ENext = None
		if self.epgcache is not None:
			ENext = self.epgcache.lookupEvent(["IBDCT", (service.toString(), 0, -1, -1)])
		if ENext:
			ENext
			maxx = 0
			for x in ENext:
				if maxx > 0:
					if x[4]:
						x[4]
						t = localtime(x[1])
						text = text + "%02d:%02d %s\n" % (t[3], t[4], x[4])
					else:
						x[4]
						text = text + "n/a\n"
				maxx += 1
				if maxx > 8:           # maximal "50" = 50 next epg/event entry´s ... you can edit this number to show more or less 
					break
					continue
		else:
			ENext
		self.text = text
		return None



