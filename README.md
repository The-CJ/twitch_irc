# Twitch irc Client

Simple to use IRC connection for Twitch optimized for the PhaazeOS project
but usable to any purpose


> Inspired by the code of Rapptz's Discord library (function names and usage)

## Usage

```py
import twitch_irc

class MyBot(twitch_irc.Client):

  async def onReady(self):
    await self.joinChannel('my_channel_name')

  async def onMessage(self, message):
    print(message.content)

    # do more with your code


x = MyBot()
x.run(token="oauth:supersecret", nickname="cool_username")
```
:copyright: 2018-2020 The_CJ
