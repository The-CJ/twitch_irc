# Twitch irc Client

Simple to use IRC connection for Twitch optimited for the PhaazeOS project
but usable to any purpose

:copyright: (c) 2018-2018 The_CJ

- Inspired by the code of Rapptz's Discord library (function names and usage)

## Usage

```
import asyncio, twitch_irc

class MyBot(twitch_irc.Client):
  async def on_message(self, message):
    print(message.content)

    # do more with your code


x = MyBot()
x.run(token="oauth:supersecret", nickname="cool_username")
```