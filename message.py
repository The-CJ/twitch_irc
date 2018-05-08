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
		user-type=mod :the__cj!the__cj@the__cj.tmi.twitch.tv PRIVMSG #phaazebot :Hello Kappa /

		into a usable class
	"""

	def __init__(self, raw_data):
		self.raw = raw_data			# str

		self.badges = [] 			# list
		self.color = None 			# str
		self.name = None 			# str
		self.display_name = None 	# str
		self.emotes = [] 			# list
		self.id = None				# str
		self.mod = False 			# bool
		self.room_id = None 		# str
		self.turbo = False 			# bool
		self.user_id = None 		# str
		self.user_type = None 		# str
		self.content = None 		# str
