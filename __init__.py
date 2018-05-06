import asyncio, time

class Client():
	def __init__(self, token=None, nickname=None):

		self.running = False

		self.token = token
		self.nickname = nickname
		self.server = "irc.twitch.tv"
		self.port = 6667
		self.last_ping = time.time()

		self.connection = None
		self.channels = {}

		self.traffic = 0

	def stop(self):
		self.running = False
		self.connection.close()

	#utils
	async def send_pong(self):
		self.connection.send(bytes("PONG :tmi.twitch.tv\r\n", 'UTF-8'))

	async def send_nick(self):
		self.connection.send(bytes("NICK {0}\r\n".format(self.nickname), 'UTF-8'))

	async def send_pass(self):
		self.connection.send(bytes("PASS {0}\r\n".format(self.token), 'UTF-8'))

	async def req_membership(self):
		self.connection.send(bytes("CAP REQ :twitch.tv/membership\r\n", 'UTF-8'))

	async def req_commands(self):
		self.connection.send(bytes("CAP REQ :twitch.tv/commands\r\n", 'UTF-8'))

	async def req_tags(self):
		self.connection.send(bytes("CAP REQ :twitch.tv/tags\r\n", 'UTF-8'))

	async def save_print_raw_data(self, data):
		b = ""
		for char in data:
			if ord(char) < 256:
				b = b + char

		print(b)

	#comms
	async def send_message(self, channel, message):
		if self.traffic <= 29:
			self.connection.send(bytes("PRIVMSG #{0} :{1}\r\n".format(channel.lower(), message), 'UTF-8'))
			self.traffic += 1
			await asyncio.sleep(20)
			self.traffic -= 1

	async def join_channel(self, channel):
		self.connection.send(bytes("JOIN #{0}\r\n".format(channel.lower()), 'UTF-8'))
		#if not channel.lower() in [c.name for c in self.channels]:
		#	self.channels.append(channel_class(self.BASE, channel))

	async def part_channel(self, channel):
		self.connection.send(bytes("PART #{0}\r\n".format(channel.lower()), 'UTF-8'))
		#if channel in [c.name for c in self.channels]:
		#	for c in self.channels:
		#		if c.name.lower() == channel.lower():
		#			self.channels.remove(c)

	async def join_all_channel(self):
		file = json.loads(open("_TWITCH_/_achtive_channels.json", "r").read())
		for channel in file.get("channels", []):
			await self.join_channel(channel)
			await asyncio.sleep(30/50)

		self.BASE.modules.Console.CYAN("INFO", "Joined: {} Twitch channels".format(str(len(file.get("channels", [])))))

	#main connection
	async def run(self):
		self.running = True
		self.last_ping = time.time()

		while self.running:

			#init connection
			self.connection = socket.socket()
			self.last_ping = time.time()

			try:
				self.connection.connect((self.server, self.port))
			except:
				self.BASE.modules.Console.RED("ERROR", "Unable to connect to the Twitch IRC")
				self.connection.close()
				self.last_ping = time.time()
				await asyncio.sleep(10)
				continue

			self.connection.settimeout(0.005)

			#login
			await self.send_pass()
			await self.send_nick()

			#get infos
			await self.req_membership()
			await self.req_commands()
			await self.req_tags()

			#join main channel
			await self.join_channel(self.nickname)
			#asyncio.ensure_future( self.join_all_channel() ) #FIXME:

			self.BASE.is_ready.twitch = True

			#listen to twitch
			while self.running:
				raw_data_bytes = ""

				disconnected = int(time.time()) - int(self.last_ping)
				if int(disconnected) > 800:
					#Twitch issn't pinging us, most likly means connection timeout --> Reconnect
					self.BASE.modules.Console.RED("ERROR", "No Twitch IRC Server response")
					self.connection.close()
					break

				try:
					raw_data_bytes = raw_data_bytes + self.connection.recv(4096).decode('UTF-8')
					raw_data = raw_data_bytes.splitlines()

					if len(raw_data) == 0:
						#Twitch send nothing, most likly means connection timeout --> Reconnect
						break

					for data in raw_data:
						#Twitch can give more than one segment in a datacluster

						#save, no Unicode debug print of all data
						#await self.save_print_raw_data(data) # DEBUG:

						#just to be sure
						if data in ["", " ", None]: continue

						#response to PING
						elif re.match(r'^PING', data) != None:
							self.last_ping = time.time()
							await self.send_pong()

						#we are connected
						elif re.match(r"^:tmi\.twitch\.tv 001.*", data) != None:
							self.BASE.modules.Console.GREEN("SUCCESS", "Twitch IRC Connected")

						#on_message
						elif re.match(r'^@.+\.tmi\.twitch\.tv PRIVMSG #.+', data) != None:
							message = OBJECT_GENERATOR.Message(data)
							asyncio.ensure_future( self.on_message(message) )

						#on_member_join
						elif re.match(r"^:tmi.+\.twitch\.tv JOIN #.+", data) != None:
							name = data.split("!")[1]
							name = name.split("@")[0]

							channel = data.split("#")[1]

							asyncio.ensure_future( self.BASE.modules._Twitch_.Base.on_member_join(self.BASE, channel, name) )

						#on_member_leave
						if "tmi.twitch.tv PART #" in data and data.startswith(":"):
							name = data.split("!")[1]
							name = name.split("@")[0]

							channel = data.split("#")[1]

							asyncio.ensure_future( self.BASE.modules._Twitch_.Base.on_member_leave(self.BASE, channel, name) )

						#on other event
						if ":tmi.twitch.tv USERNOTICE #" in data and data.startswith("@"):
							event = re.search(r"msg-id=(.*?);", data)
							if event != None:
								event = event.group(1)

							#Sub event
							if event in ["resub","sub"]:

								try:
									sub_message = Get_classes_from_data.Twitch_sub(data)
									asyncio.ensure_future( self.BASE.modules._Twitch_.Base.on_sub(self.BASE, sub_message) )
								except:
									self.BASE.modules.Console.RED("ERROR", "Failed to process Twitch Sub")
									continue

							#Raid event
							if event in ["raid"]:
								return #TODO: Make something with this
								try:
									raid__message = Get_classes_from_data.Twitch_sub(data)
									asyncio.ensure_future( self.BASE.modules._Twitch_.Base.on_raid(self.BASE, raid__message) )
								except:
									self.BASE.modules.Console.RED("ERROR", "Failed to process Twitch Sub")
									continue


				except socket.timeout:
					await asyncio.sleep(0.025)

			self.BASE.is_ready.twitch = False

	#events
	async def on_message(self, message):
		pass
