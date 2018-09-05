import re

class Channel(object):
	"""This class is generated when the bot join's a chat room or some kind of channel update happen,

		`raw_data` = type :: str

		@
		broadcaster-lang=;
		emote-only=0;
		followers-only=-1;
		r9k=0;
		rituals=0;
		room-id=94638902;
		slow=0;
		subs-only=0 :tmi.twitch.tv ROOMSTATE #phaazebot

		into a usable class and adds it to the bots self.channels dict
	"""

	def __init__(self, raw_data):
		self.raw = raw_data.strip('@')	# str

		self.broadcaster_lang = None 	# str
		self.emote_only = None 			# bool
		self.followers_only = None		# int
		self.r9k = None					# bool
		self.rituals = None				# bool
		self.id = None					# str
		self.slow = None				# int
		self.subs_only = None			# bool
		self.name = None				# str

		self.users = dict()				# dict

		self.process()
		del self.raw

	def process(self):
		self.raw = self.raw.strip('@')

		#broadcaster_lang
		search = re.search(r'broadcaster-lang=(.*?)[; ]', self.raw)
		if search != None:
			self.broadcaster_lang = str( search.group(1) )

		#emote_only
		search = re.search(r'emote-only=(1|0)[; ]', self.raw)
		if search != None:
			if search.group(1) == "1":
				self.emote_only = True
			elif search.group(1) == "0":
				self.emote_only = False

		#folloers_only
		search = re.search(r'followers-only=(\d+?|-1)[; ]', self.raw)
		if search != None:
			self.followers_only = int( search.group(1) )

		#r9k
		search = re.search(r'r9k=(1|0)[; ]', self.raw)
		if search != None:
			if search.group(1) == "1":
				self.r9k = True
			elif search.group(1) == "0":
				self.r9k = False

		#rituals
		search = re.search(r'rituals=(1|0)[; ]', self.raw)
		if search != None:
			if search.group(1) == "1":
				self.rituals = True
			elif search.group(1) == "0":
				self.rituals = False

		#id
		search = re.search(r'room-id=(\d+?)[; ]', self.raw)
		if search != None:
			self.id = str( search.group(1) )

		#slow
		search = re.search(r'slow=(\d+?)[; ]', self.raw)
		if search != None:
			self.slow = int( search.group(1) )

		#subs_only
		search = re.search(r'subs-only=(1|0)[; ]', self.raw)
		if search != None:
			if search.group(1) == "1":
				self.subs_only = True
			elif search.group(1) == "0":
				self.subs_only = False

		#name
		search = re.search(r'ROOMSTATE #(\w+)', self.raw)
		if search != None:
			self.name = search.group(1)

	def update(self, new_cannel):
		""" together with a new channel object, it updates all attributes that are not None """
		if type(new_cannel) != Channel:
			raise AttributeError(f'channel must be "{str(Channel)}" not "{type(channel)}"')

		__all__ = dir(new_cannel)
		__all__ = [attr for attr in __all__ if not attr.startswith('__') and attr != "users"]
		for attr in __all__:

			if not callable( getattr(self, attr) ):

				new_value = getattr(new_cannel, attr, None)
				if new_value != None:
					setattr(self, attr, new_value)

