# Twitch irc Client

Simple to use IRC connection for Twitch optimized for the PhaazeOS project
but usable to any purpose


> Inspired by the code of Rapptz's Discord library (function names and usage)

## Install

There are many ways. here my "prefered" one:
```
py -m pip install git+https://github.com/The-CJ/twitch_irc.py.git#egg=twitch_irc
```

## Example

```py
import twitch_irc

class MyBot(twitch_irc.Client):

  async def onReady(self):
    await self.joinChannel('my_channel_name')

  async def onMessage(self, message):
    print(message.content)

    # do more with your code


x = MyBot(token="oauth:supersecret", nickname="cool_username")
x.run()
```
:copyright: 2018-2021 The_CJ
