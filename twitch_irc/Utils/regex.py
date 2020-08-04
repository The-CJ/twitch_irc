import re

# Includes a precompiled re objects for every IRC event

RePing:"re.Pattern" = re.compile(r"^PING.*")
ReOnReady:"re.Pattern" = re.compile(r"^:tmi\.twitch\.tv 001.*")
ReGarbage:"re.Pattern" = re.compile(r"^:tmi\.twitch\.tv (002|003|004|375|372|376|CAP).*")

ReWrongAuth:"re.Pattern" = re.compile(r'^:tmi\.twitch\.tv NOTICE \* :Login.*')

ReJoin:"re.Pattern" = re.compile(r"^.+\.tmi\.twitch\.tv JOIN #.+")
RePart:"re.Pattern" = re.compile(r"^.+\.tmi\.twitch\.tv PART #.+")
ReRoomState:"re.Pattern" = re.compile(r"^@.+:tmi\.twitch\.tv ROOMSTATE #.+")
ReClearChat:"re.Pattern" = re.compile(r"^@.+:tmi\.twitch\.tv CLEARCHAT #.+")
RePrivMessage:"re.Pattern" = re.compile(r"^@.+\.tmi\.twitch\.tv PRIVMSG #.+")
