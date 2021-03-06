from redbot.core import commands as cmd

COLOR = 0xF495BF

class RoleConverter(cmd.RoleConverter):
    def __init__(self):
        super(self.__class__, self).__init__()

    async def convert_(self, ctx:cmd.Context, argument:str):
        try:
            return await self.convert(ctx, argument)
        except:
            return None

class EmojiConverter(cmd.EmojiConverter):
    def __init__(self):
        super(self.__class__, self).__init__()

    async def convert_(self, ctx:cmd.Context, argument:str):
        try:
            return await self.convert(ctx, argument)
        except:
            return None

class TextChannelConverter(cmd.TextChannelConverter):
    def __init__(self):
        super(self.__class__, self).__init__()

    async def convert_(self, ctx:cmd.Context, argument:str):
        try:
            return await self.convert(ctx, argument)
        except:
            return None