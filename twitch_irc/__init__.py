# -*- coding: utf-8 -*-

"""
##################
Twitch IRC wrapper
##################

Simple to use IRC connection for Twitch optimized for the PhaazeOS project
but usable to any purpose

:copyright: (c) 2018-2020 The_CJ
:license: MIT License

- Inspired by the code of Rapptz's Discord library

"""

__title__ = 'twitch_irc'
__author__ = 'The_CJ'
__license__ = 'MIT'
__copyright__ = 'Copyright 2018-2020 The_CJ'
__version__ = "1.1.0"

from .Classes.badge import Badge
from .Classes.bitsbadgetier import BitsBadgeTier
from .Classes.channel import Channel
from .Classes.client import Client
from .Classes.emote import Emote
from .Classes.message import Message
from .Classes.mysterygiftsub import MysteryGiftSub
from .Classes.raid import Raid
from .Classes.resub import ReSub, GiftPaidUpgrade, PrimePaidUpgrade, StandardPayForward, CommunityPayForward
from .Classes.reward import Reward
from .Classes.ritual import Ritual
from .Classes.sub import Sub, GiftSub
from .Classes.timeout import Timeout, Ban
from .Classes.user import User
from .Classes.userstate import UserState

class Errors(object):
	from .Utils.errors import InvalidAuth, InvalidCredentials, PingTimeout, EmptyPayload
