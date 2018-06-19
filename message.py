import re

class Message(object):
	"""This class is generated when a user is sending a message, it turns raw data like:

		`raw_data` = type :: str

		@
		badges=moderator/1,premium/1;
		color=#696969;
		display-name=The__CJ;
		emotes=25:6-10;
		id=13e484e8-1d0d-44c0-8b1e-03d76b636688;
		mod=1;
		room-id=94638902;
		subscriber=0;
		tmi-sent-ts=1525706672840;
		turbo=0;
		user-id=67664971;
		user-type=mod
		:the__cj!the__cj@the__cj.tmi.twitch.tv
		PRIVMSG #phaazebot :Hello Kappa /

		into a usable class
	"""

	def __init__(self, raw_data):
		self.raw = raw_data.strip('@')				# str

		self.badges = [] 							# list
		self.color = None 							# str
		self.display_name = None 					# str
		self.name = None 							# str
		self.emotes = [] 							# list
		self.channel_id = None						# str
		self.channel_name = None					# str
		self.user_id = None 						# str
		self.user_type = None 						# str
		self.sub = False 							# bool
		self.mod = False 							# bool
		self.turbo = False 							# bool
		self.content = None 						# str

		self.process()
		del self.raw

	def process(self):
		#badges
		search = re.search(r'badges=(.+?)[; ]', self.raw)
		if search != None:
			self.badges = search.group(1).split(',')

		#color
		search = re.search(r'color=#(.+?)[; ]', self.raw)
		if search != None:
			self.color = search.group(1)

		#display_name
		search = re.search(r'display-name=(.+?)[; ]', self.raw)
		if search != None:
			self.display_name = search.group(1)

		#name
		search = re.search(r'!(.+?)@', self.raw)
		if search != None:
			self.name = search.group(1)

		#emotes
		search = re.search(r'emotes=(.+?)[; ]', self.raw)
		if search != None:
			try:
				e = search.group(1).split('/')
				for emote in e:
					id_, amount = emote.split(":", 1)
					em = dict(id= id_, amount= len(amount.split(",")))
					self.emotes.append( em )
			except:
				self.emotes = []

		#channel_id
		search = re.search(r'room-id=(.+?)[; ]', self.raw)
		if search != None:
			self.channel_id = search.group(1)

		#channel_name
		search = re.search(r'PRIVMSG #(.+?) :', self.raw)
		if search != None:
			self.channel_name = search.group(1)

		#user_id
		search = re.search(r'user-id=(.+?)[; ]', self.raw)
		if search != None:
			self.user_id = search.group(1)

		#user_type
		search = re.search(r'user-type=(.+?)[; ]', self.raw)
		if search != None:
			self.user_type = search.group(1)

		#sub
		search = re.search(r'subscriber=(0|1)[; ]', self.raw)
		if search != None:
			if search.group(1) == "1":
				self.sub = True
			else:
				self.sub = False

		#mod
		search = re.search(r'mod=(0|1)[; ]', self.raw)
		if search != None:
			if search.group(1) == "1":
				self.mod = True
			else:
				self.mod = False

		#turbo
		search = re.search(r'turbo=(0|1)[; ]', self.raw)
		if search != None:
			if search.group(1) == "1":
				self.turbo = True
			else:
				self.turbo = False

		#content
		search = re.search(r'PRIVMSG #.+? :(.+)', self.raw)
		if search != None:
			self.content = search.group(1).strip('\r')

