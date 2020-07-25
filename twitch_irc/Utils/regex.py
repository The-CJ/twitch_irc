import re

# Includes a precompiled re objects for every IRC event

RePing:"re.Pattern" = re.compile(r"^PING.*")
ReWrongAuth:"re.Pattern" = re.compile(r'^:tmi\.twitch\.tv NOTICE \* :Login.*')
ReChannelUpdate:"re.Pattern" = re.compile(r"^@.+:tmi\.twitch\.tv ROOMSTATE #.+")

ReOnReady:"re.Pattern" = re.compile(r"^:tmi\.twitch\.tv 001.*")
ReOnMemberJoin:"re.Pattern" = re.compile(r"^.+\.tmi\.twitch\.tv JOIN #.+")
ReOnMemberLeft:"re.Pattern" = re.compile(r"^.+\.tmi\.twitch\.tv PART #.+")
ReOnMessage:"re.Pattern" = re.compile(r"^@.+\.tmi\.twitch\.tv PRIVMSG #.+")
