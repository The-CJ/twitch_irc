import re
from .regex import Regex

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
		search = re.search(Regex.Channel.broadcaster_lang, self.raw)
		if search != None:
			self.broadcaster_lang = str( search.group(1) )

		#emote_only
		search = re.search(Regex.Channel.emote_only, self.raw)
		if search != None:
			if search.group(1) == "1":
				self.emote_only = True
			elif search.group(1) == "0":
				self.emote_only = False

		#folloers_only
		search = re.search(Regex.Channel.folloers_only, self.raw)
		if search != None:
			self.followers_only = int( search.group(1) )

		#r9k
		search = re.search(Regex.Channel.r9k, self.raw)
		if search != None:
			if search.group(1) == "1":
				self.r9k = True
			elif search.group(1) == "0":
				self.r9k = False

		#rituals
		search = re.search(Regex.Channel.rituals, self.raw)
		if search != None:
			if search.group(1) == "1":
				self.rituals = True
			elif search.group(1) == "0":
				self.rituals = False

		#room_id | id
		search = re.search(Regex.Channel.room_id, self.raw)
		if search != None:
			self.id = str( search.group(1) )

		#slow
		search = re.search(Regex.Channel.slow, self.raw)
		if search != None:
			self.slow = int( search.group(1) )

		#subs_only
		search = re.search(Regex.Channel.subs_only, self.raw)
		if search != None:
			if search.group(1) == "1":
				self.subs_only = True
			elif search.group(1) == "0":
				self.subs_only = False

		#room_name | name
		search = re.search(Regex.Channel.room_name, self.raw)
		if search != None:
			self.name = search.group(1)

	def update(self, new_cannel):
		""" together with a new channel object, it updates all attributes that are not None """
		if type(new_cannel) != Channel:
			raise AttributeError(f'channel must be "{str(Channel)}" not "{type(new_cannel)}"')

		__all__ = dir(new_cannel)
		__all__ = [attr for attr in __all__ if not attr.startswith('__') and attr != "users"]
		for attr in __all__:

			if not callable( getattr(self, attr) ):

				new_value = getattr(new_cannel, attr, None)
				if new_value != None:
					setattr(self, attr, new_value)

