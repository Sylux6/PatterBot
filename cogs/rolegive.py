from redbot.core import commands as cmd
from redbot.core import Config as Cfg
from discord import Reaction, Member, Embed, Emoji
from utils.imports import EmojiConverter, RoleConverter, COLOR

class Rolegive(cmd.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Cfg.get_conf(self, 667)

        default = {
            "title": "React with corresponding emoji to get role!",
            "message": 0,
            "associations": list()
        }

        self.config.register_guild(**default)
    
    def check_message(self, reaction:Reaction):
        return reaction.message.id is self.config.guild(reaction.message.guild).message() and not reaction.me

    async def edit_role_list(self, reaction:Reaction, member:Member, change_type):
        associations = await self.config.guild(member.guild).associations()
        match = [asso for asso in associations if asso[0] == str(reaction.emoji)]

        if match:
            asso = match[0]
            role = member.guild.get_role(asso[1])

            if role is None:
                print("ROLE_ATTRIBUTION_ERROR: role {} doesn't exist anymore.".format(asso[1]))
            else:
                roles = [r for r in member.roles if r != role] if change_type is 'r' else list(member.roles) + [role]
                await member.edit(roles= roles)
        
        else: print("WRONG_REACTION: {} not in assosiation list.".format(str(reaction.emoji)))


    @cmd.check(check_message)
    async def on_reaction_add(self, reaction:Reaction, member:Member):
        await self.edit_role_list(reaction, member, 'a')
    
    @cmd.check(check_message)
    async def on_reaction_remove(self, reaction:Reaction, member:Member):
        await self.edit_role_list(reaction, member, 'r')

    @cmd.group(name= 'rolegive')
    async def rolegive_group(self, ctx:cmd.Context):
        pass
    
    @cmd.admin()
    @rolegive_group.command(name= 'title')
    async def rolegive_title(self, ctx:cmd.Context, *, text):
        """
        **[text]** : edits the role message's title.
        """
        text = text.replace("\\n", "\n")

        try:
            embed = Embed(title= "Title changed - example:",
                          color= COLOR,
                          description= text.format(ctx.author))
            await self.config.guild(ctx.guild).title.set(text)
            
        except AttributeError:
            embed = Embed(title= "Error",
                          color= COLOR,
                          description= "Wrong attribute.")
        except IndexError:
            embed = Embed(title= "Error",
                          color= COLOR,
                          description= "Wrong format.")
        
        finally:
            await ctx.send(embed= embed)
    
    @cmd.admin()
    @rolegive_group.command(name= 'add')
    async def rolegive_add(self, ctx:cmd.Context, emoji:str, *, role):
        """
        **[emoji] [role]** : associates an emoji with a role.
        """
        associations, items, emoji, role = await self.import_rolegive_data(ctx, emoji, role)
        
        passed = False
        if role is None:
            embed = Embed(title= "Error",
                          color= COLOR,
                          description= "Failed to load role.")
        elif emoji is None:
            embed = Embed(title= "Error",
                          color= COLOR,
                          description= "Failed to load emoji.")
        elif items:
            if str(emoji) in items[0]:
                embed = Embed(title= "Error",
                              color= COLOR,
                              description= "Emoji already in association list.")
            elif role.id in items[1]:
                embed = Embed(title= "Error",
                              color= COLOR,
                              description= "Role already in association list.")
            else: passed = True
        else: passed = True
        
        if passed:
            associations.append([str(emoji), role.id])
            await self.config.guild(ctx.guild).associations.set(associations)
            m = "{} successfully linked with {}".format(str(emoji), role)

            state = await self.edit_rolegive_message(ctx, emoji, 'a')

            embed = Embed(title= await self.config.guild(ctx.guild).title(),
                          color= COLOR,
                          description= state.format(m))
     
        await ctx.send(embed= embed)

    @cmd.admin()
    @rolegive_group.command(name= 'remove')
    async def rolegive_remove(self, ctx:cmd.Context, element:str):
        """
        **[emoji or role]** : removes an association from the list.
        """
        associations, items, emoji, role = await self.import_rolegive_data(ctx, element, element)

        if not items:
            embed = Embed(title= "Error",
                          color= COLOR,
                          description= "No association made yet.")

        elif emoji is not None:
            comp_var = 0
            element_var = str(emoji)
        elif role is not None:
            comp_var = 1
            element_var = role.id
        else:
            comp_var = 0
            element_var = -1
        
        if element_var not in items[comp_var]:
            embed = Embed(title= "Error",
                          color= COLOR,
                          description= "Reference not found.")

        else:
            for asso in associations:
                if element_var == asso[comp_var]:
                    associations.remove(asso)
                    break
            await self.config.guild(ctx.guild).associations.set(associations)

            message = await ctx.get_message(await self.config.guild(ctx.guild).message())
            emoji = await EmojiConverter().convert_(ctx, asso[0])
            role = ctx.guild.get_role(asso[1])
            m = "Association between {} and {} removed successfully.".format(emoji, role)

            state = await self.edit_rolegive_message(ctx, emoji, 'r')

            embed = Embed(title= await self.config.guild(ctx.guild).title(),
                          color= COLOR,
                          description= state.format(m))
        
        await ctx.send(embed= embed)

    @cmd.admin()
    @rolegive_group.command(name= 'set')
    async def rolegive_set(self, ctx:cmd.Context):
        """
        : sends the rolegive message members can react on.
        """
        embed = Embed(title= await self.config.guild(ctx.guild).title(),
                      color= COLOR,
                      description= await self.make_rolegive_message(ctx))
        message = await ctx.send(embed = embed)

        await self.config.guild(ctx.guild).message.set(message.id)

        associations = await self.config.guild(ctx.guild).associations()
        [await message.add_reaction(emoji) for emoji in [await EmojiConverter().convert_(ctx, asso[0]) for asso in associations] if emoji is not None]

    @cmd.mod()
    @rolegive_group.command(name= 'show')
    async def rolegive_show(self, ctx:cmd.Context):
        """
        : shows the associations between emojis and role.
        """
        m = await self.make_rolegive_message(ctx)
        
        if m:
            embed = Embed(title= "Associations",
                          color= COLOR,
                          description= m)
        else:
            embed = Embed(title= "Error",
                          color= COLOR,
                          description= "No association made yet.")
        
        await ctx.send(embed= embed)
    
    @cmd.admin()
    @rolegive_group.command(name= 'reset')
    async def rolegive_reset(self, ctx:cmd.Context):
        """
        : resets the associations list.
        """
        embed = Embed(title= "Confirm?",
                      color= COLOR,
                      description= "Write y/n to confirm removal.")
        await ctx.send(embed= embed)

        def check(m):
            if m.channel != ctx.channel or m.author != ctx.message.author:
                return False
            elif m.content.lower()[0] not in "yn":
                return False
            else:
                return True
        
        confirm = await self.bot.wait_for('message', check= check)

        if confirm.content.lower().startswith("y"):
            await self.config.guild(ctx.guild).associations.set(list())
            embed = Embed(title= "Reset.",
                          color= COLOR,
                          description= "Association list has been reset.")
        else:
            embed = Embed(title= "Cancelled",
                          color= COLOR,
                          description= "Reset cancelled.")
        await ctx.send(embed= embed)
    
    @cmd.command(name= 'test')
    async def test_(self, ctx):
        await ctx.send("a")

    async def import_rolegive_data(self, ctx:cmd.Context, emoji:str, role:str):
        emoji = await EmojiConverter().convert_(ctx, emoji)
        role  = await RoleConverter().convert_(ctx, role)

        associations = await self.config.guild(ctx.guild).associations()
        items = [l for l in zip(*associations)]

        return associations, items, role, emoji

    async def make_rolegive_message(self, ctx:cmd.Context):
        associations = await self.config.guild(ctx.guild).associations()

        async def aux(emoji, role):
            return "{} - {}".format(await EmojiConverter().convert_(ctx, emoji),
                                    await RoleConverter().convert_(ctx, str(role)))
        
        message = "\n".join([await aux(emoji, role) for emoji, role in associations]).replace("None", "Not found")

    async def edit_rolegive_message(self, ctx:cmd.Context, emoji:Emoji, edit_type:str):
        try:
            message = await ctx.get_message(await self.config.guild(ctx.guild).message())
            embed = Embed(title= await self.config.guild(ctx.guild).title(),
                          color= COLOR,
                          description= await self.make_rolegive_message(ctx))
            await message.edit(embed= embed)

            if edit_type is 'a':
                await message.add_reaction(emoji)
            elif edit_type is 'r':
                reaction = [r for r in message.reactions if r.emoji == emoji][0]
                async for user in reaction.users():
                    await message.remove_reaction(reaction.emoji, user)

            return "{}\nMessage updated."

        except:
            return "{}"
        return message if message else "No association made yet."


def setup(bot):
    bot.add_cog(Rolegive(bot))