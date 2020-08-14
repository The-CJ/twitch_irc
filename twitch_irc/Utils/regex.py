import re

# Includes a precompiled re objects for every IRC event

RePing:"re.Pattern" = re.compile(r"^PING.*")
ReOnReady:"re.Pattern" = re.compile(r"^:tmi\.twitch\.tv 001.*")
ReGarbage:"re.Pattern" = re.compile(r"^.*tmi\.twitch\.tv (002|003|004|366|372|375|376|CAP).*")
ReUserList:"re.Pattern" = re.compile(r"^.*tmi\.twitch\.tv 353.*")

ReWrongAuth:"re.Pattern" = re.compile(r'^:tmi\.twitch\.tv NOTICE \* :Login.*$')

ReJoin:"re.Pattern" = re.compile(r"^.+tmi\.twitch\.tv JOIN #.+$")
RePart:"re.Pattern" = re.compile(r"^.+tmi\.twitch\.tv PART #.+$")
ReRoomState:"re.Pattern" = re.compile(r"^.+tmi\.twitch\.tv ROOMSTATE #.+$")
ReClearChat:"re.Pattern" = re.compile(r"^.+tmi\.twitch\.tv CLEARCHAT #.+$")
ReUserState:"re.Pattern" = re.compile(r"^.+tmi\.twitch\.tv USERSTATE #.+$")
ReClearMsg:"re.Pattern" = re.compile(r"^.+tmi\.twitch\.tv CLEARMSG #.+$")
RePrivMessage:"re.Pattern" = re.compile(r"^.+tmi\.twitch\.tv PRIVMSG #.+$")
ReUserNotice:"re.Pattern" = re.compile(r"^.+tmi\.twitch\.tv USERNOTICE #.+$")
