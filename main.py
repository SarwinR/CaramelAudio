import discord
from discord.ext import commands, tasks
import asyncio
import os
from replit import db
from keep_alive import keep_alive

#add mute / deafen

#del db["822418452702691338"]

client = commands.Bot(command_prefix=('c. ', 'C. ', 'C.', 'c.'))
client.remove_command('help')

guild_ids = []
member_ids = []
text_channel_ids = []
voice_channel_ids = []
done_inputs = []

userGenerated = []
userGeneratedChannels = []

def request_template_channel(id):
    template_channels = []
    try:
        template_channels = db[str(id)]
    except:
        pass

    return template_channels


def request_user_channel(id):
    global userGenerated
    global userGeneratedChannels

    index = None
    for i in range(len(userGenerated)):
        if (str(id) == str(userGenerated[i])):
            index = i
            break

    if (index != None):
        return userGeneratedChannels[index]
    else:
        return None


async def send_welcome_msg(channel):
    embed = discord.Embed(
        title="__**HOW TO SETUP THE BOT**__",
        description=
        "-- -- -- -- --\n**My prefix is [`c.`]**\n-- -- -- -- --\n**[1]**\n__**Set an Output Channel**__ - It is a channel where the Bot will receive commands from Users and output messages \n[`c.output #channel`]\n-- -- -- -- --\n**[2]**\n__**Set a Template Channe]**__ - It is a Voice Channel that will be used as a Template. Each time a user request a Voice Channel the Template Channel will be cloned. It is also the channel that user needs to join so that a  Voice Channel is created \n[`c.addtemplate`]\n-- -- -- -- --\n**[3]**\nCongratulation you are good to go. You can get a list of Template Channels on your server by using the command \n[`c.templatelist`]\n-- -- -- -- --\n**[4]**\nYou can do [`c.help`] to get the list of commands used to setup the Bot or [`c.cmd`] to get a list of commands used to customize your Voice Channel\n-- -- -- -- --\n**[5]**\nThanks for choosing Caramel Audio\n-- -- -- -- --",
        color=0xffbb00)
    embed.add_field(
        name="Still Having Problems?",
        value=
        "[Join the Support Server](https://discord.gg/WysSQg2njs)\nor\n[Check the Website](https://caramelaudiowebsite.sarwin.repl.co/index.html)",
        inline=True)
    embed.set_footer(text="Made with ❤️ by Sarwin")
    await channel.send(embed=embed)


async def RequestTemplateList(ctx):
    msg = await ctx.send("Fetching data. Hold on.")
    guild_id = ctx.channel.guild.id

    template_channels = request_template_channel(str(guild_id))

    channelList = "{} This server has `{}` Template Channels : \n".format(
        ctx.author.mention,
        len(template_channels) - 1)
    for i in range(len(template_channels)):
        if (i != 0):
            channelList += "`{}` ".format(
                client.get_channel(int(template_channels[i])).name)

    if (len(template_channels) == 1):
        await msg.edit(
            content=
            "{} this server has `no` Template Channels. Use `c.help` for info".
            format(ctx.author.mention))
    else:
        if (len(template_channels) == 0):
            await msg.edit(
                content=
                "{} this server has not yet setup the **Output Channel**. Use `c.help` for info"
                .format(ctx.author.mention))
        else:
            await msg.edit(content=channelList)


async def AddVoiceTemplate(member, before, after):
    global guild_ids
    global member_ids
    global done_inputs

    for index in range(len(guild_ids)):
        if (str(after.channel.guild.id) == guild_ids[index]):
            if (str(member.id) == member_ids[index]):
                if (done_inputs[index] == False):
                    done_inputs[index] == True

                    global voice_channel_ids
                    global text_channel_ids

                    voice_channel_ids[index] = after.channel.id

                    process_msg = "`{}` is being resistered as a Channel Template. Hold on.".format(
                        after.channel.name)

                    done_msg = "`{}` has been set as a Voice Channel Template. Join it to see the magic. Use [`c.cmd`] to see the options avaiable".format(
                        after.channel.name)

                    msg = await client.get_channel(int(text_channel_ids[index])
                                                   ).send(process_msg)

                    template_channels = request_template_channel(
                        guild_ids[index])

                    flag = False

                    if (len(template_channels) != 0):
                        for i in range(len(template_channels)):
                            if (template_channels[i] ==
                                    voice_channel_ids[index]):
                                flag = True
                                error_msg = "You are trying to add `{}`, but it is already a Channel Template. Do [`c.templatelist`] to get a list of all channels that have been setup as Channel Template".format(
                                    after.channel.name)
                                await msg.edit(content=error_msg)
                                break
                        if (flag == False):
                            template_channels.append(voice_channel_ids[index])
                            db[guild_ids[index]] = template_channels
                            await msg.edit(content=done_msg)

                    else:
                        template_channels.append(voice_channel_ids[index])
                        db[guild_ids[index]] = template_channels
                        await msg.edit(content=done_msg)

                    del guild_ids[index]
                    del member_ids[index]
                    del voice_channel_ids[index]
                    del text_channel_ids[index]
                    del done_inputs[index]

                    await member.move_to(None)


async def SetOutputChannel(ctx, channel):
    guild_id = channel.guild.id
    template_channels = request_template_channel(str(guild_id))

    msg = ""

    if (len(template_channels) != 0):
        last_channel = client.get_channel(int(template_channels[0]))
        if (str(last_channel.id) != str(channel.id)):
            msg = "{} Output Channel has been switch from {} to {}".format(
                ctx.author.mention, last_channel.mention, channel.mention)
            template_channels[0] = str(channel.id)
            db[str(guild_id)] = template_channels

        else:
            msg = "{}, {} is already the Output Channel".format(
                ctx.author.mention, channel.mention)

    else:
        template_channels.append(channel.id)
        msg = "{} Output Channel has been set to {}".format(
            ctx.author.mention, channel.mention)
        db[str(guild_id)] = template_channels

    await ctx.send(msg)


async def GenerateChannel(member, before, after, template_channels):
    global userGenerated
    global userGeneratedChannels

    flag = False
    vc_id = ""
    output_channel = client.get_channel(int(template_channels[0]))

    for i in range(len(userGenerated)):
        if (str(member.id) == str(userGenerated[i])):
            flag = True
            vc_id = userGeneratedChannels[i]
            break

    if (flag == False):
        vc_name = "{}'s Voice Channel".format(member.name)
        vc_reason = "{} requested a voice channel".format(member.name)
        vc = await after.channel.clone(name=vc_name, reason=vc_reason)
        await member.move_to(vc)

        userGenerated.append(member.id)
        userGeneratedChannels.append(vc.id)

        await output_channel.send(
            "{} your voice channel have been created. Do `c.cmd` to get a list of customisation commands for your Voice Channel"
            .format(member.mention))

    else:
        vc = client.get_channel(int(vc_id))
        await member.move_to(vc)


@client.event
async def on_ready():
    print("Bot ready")


@client.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await send_welcome_msg(channel)
            break


@client.event
async def on_guild_remove(guild):
    try:
        del db[str(guild.id)]
    except:
        pass


@client.event
async def on_voice_state_update(member, before, after):
    global guild_ids

    if (after.channel == None or after.channel != before.channel):
        try:
            template_channels = request_template_channel(str(before.channel.guild.id))
            output_channel = client.get_channel(int(template_channels[0]))

            global userGenerated
            global userGeneratedChannels
            for i in range(len(userGenerated)):
                if (str(member.id) == str(userGenerated[i])):
                    await output_channel.send(
                        "{} you have left your channel. You will **lose** ownership in `30` seconds if you do not rejoin"
                        .format(member.mention))

                    vc = client.get_channel(int(userGeneratedChannels[i]))

                    await asyncio.sleep(30)
                    if (len(vc.members) == 0):
                        try:
                            userGenerated.remove(member.id)
                            await output_channel.send(
                                "{} your Voice Channel has been **deleted** due to inactivity"
                                .format(member.mention))
                            userGeneratedChannels.remove(vc.id)

                            await vc.delete(reason="It was unused")
                        except:
                            pass

                    else:
                        flag = False
                        for i in vc.members:
                            if (i.id == member.id):
                                flag = True
                                break

                        if (flag == False):
                            flag2 = False
                            for i in range(len(vc.members)):
                                if (vc.members[i].bot == False):
                                    flag2 = True
                                    owner = vc.members[i]
                                    userGenerated.remove(member.id)
                                    userGeneratedChannels.remove(vc.id)

                                    userGenerated.append(owner.id)
                                    userGeneratedChannels.append(vc.id)

                                    await output_channel.send(
                                        "`{}` is now **managed** by {}. Do `c.cmd` to get a list of customization commands for your Voice Channel"
                                        .format(vc.name, owner.mention))
                                    break

                            if (flag2 == False):
                                try:
                                    userGenerated.remove(member.id)
                                    await output_channel.send(
                                        "{} your Voice Channel has been **deleted** due to inactivity"
                                        .format(member.mention))
                                    userGeneratedChannels.remove(vc.id)

                                    await vc.delete(reason="It was unused")
                                except:
                                    pass
        except:
            pass

    if (before.channel != after.channel and after.channel != None):
        if (before.channel == None and len(guild_ids) != 0):
            await AddVoiceTemplate(member, before, after)
        else:
            guild_id = after.channel.guild.id
            template_channels = []
            try:
                template_channels = db[str(guild_id)]
            except:
                pass

            if (len(template_channels) != 0):
                for id in template_channels:
                    if (str(id) == str(after.channel.id)):
                        await GenerateChannel(member, before, after,
                                              template_channels)


@client.command()
@commands.has_permissions(manage_channels=True)
async def addtemplate(ctx):
    global guild_ids
    global member_ids
    global voice_channel_ids
    global text_channel_ids
    global done_inputs

    template_channels = request_template_channel(str(ctx.channel.guild.id))

    if (len(template_channels) == 0):
        msg = "{} this server has not setup the Output Channel yet. Use [`c.output #channel`] to set it up.".format(
            ctx.author.mention)
        await ctx.send(msg)

    else:
        await ctx.send(
            "{} **enter the Voice Channel that you wish to set as the template**."
            .format(ctx.author.mention))

        guildID = ctx.channel.guild.id

        guild_ids.append(str(guildID))
        member_ids.append(str(ctx.author.id))
        text_channel_ids.append(str(ctx.channel.id))
        voice_channel_ids.append("-")
        done_inputs.append(False)

        await asyncio.sleep(20)

        for id in guild_ids:
            if (id == "guildID"):
                await ctx.send("Timeout")
                break


@client.command()
@commands.has_permissions(manage_channels=True)
async def reset(ctx, confirm: str = ""):
    if (confirm == "CONFIRM"):
        try:
            del db[str(ctx.channel.guild.id)]
        except:
            pass
        await ctx.send("{}** all server settings have been cleared**".format(
            ctx.author.mention))
    else:
        await ctx.send(
            "{}** do `c.reset CONFIRM` WARNING: ALL YOUR SERVER'S DATA WILL BE RESET**"
            .format(ctx.author.mention))


@client.command()
@commands.has_permissions(manage_channels=True)
async def templatelist(ctx):
    await RequestTemplateList(ctx)


@client.command()
@commands.has_permissions(manage_channels=True)
async def output(ctx, channel: discord.TextChannel):
    error_msg = ""

    if (channel.permissions_for(channel.guild.me).send_messages):
        if (channel.permissions_for(channel.guild.me).read_messages):
            await SetOutputChannel(ctx, channel)
        else:
            error_msg = "{} I **cannot read messages** in `{}`. I need `permissions.read_messages` to access user's commands.".format(
                ctx.author.mention, channel.name)
    else:
        error_msg = "{} I **cannot send messages** in `{}`. I need `permissions.send_messages` to reply to user's commands.".format(
            ctx.author.mention, channel.name)

    if (error_msg != ""):
        await ctx.send(error_msg)


@client.command()
async def name(ctx, name: str):
    id = request_user_channel(ctx.author.id)
    output_channels = request_template_channel(str(ctx.channel.guild.id))
    output_channel = client.get_channel(int(output_channels[0]))

    if (id != None):
        v_channel = client.get_channel(int(id))
        v_name = v_channel.name

        await v_channel.edit(name=name)
        await output_channel.send(
            "{} your Voice Channel was **renamed** from `{}` to `{}`".format(
                ctx.author.mention, v_name, name))
    else:
        await output_channel.send(
            "{} you currently **do not own** any Voice Channel".format(
                ctx.author.mention))


@client.command()
async def bitrate(ctx, bitrate: int):
    id = request_user_channel(ctx.author.id)
    output_channels = request_template_channel(str(ctx.channel.guild.id))
    output_channel = client.get_channel(int(output_channels[0]))

    if (id != None):
        bit = bitrate
        v_channel = client.get_channel(int(id))
        v_rate = v_channel.bitrate
        rate_limit = ctx.channel.guild.bitrate_limit

        if (bitrate > int(rate_limit)):
            bit = rate_limit
        else:
            if (bitrate < 8000):
                bit = 8000

        await v_channel.edit(bitrate=bit)
        await output_channel.send(
            "{}, the **bitrate** of your Voice Channel was changed from `{}` to `{}`"
            .format(ctx.author.mention, v_rate, int(bit)))
    else:
        await output_channel.send(
            "{} you currently **do not own* any Voice Channel".format(
                ctx.author.mention))


@client.command()
async def userlimit(ctx, limit: int):
    id = request_user_channel(ctx.author.id)
    output_channels = request_template_channel(str(ctx.channel.guild.id))
    output_channel = client.get_channel(int(output_channels[0]))

    if (id != None):
        num = limit
        v_channel = client.get_channel(int(id))
        v_limit = v_channel.user_limit
        if (v_limit == 0):
            v_limit = "no limit"

        num_msg = str(limit)

        if (limit > 99):
            num = 99
            num_msg = "99"
        else:
            if (limit < 0):
                num = 0
                num_msg = "no limit"

        await v_channel.edit(user_limit=num)
        await output_channel.send(
            "{} the **user limit** of your Voice Channel was changed from `{}` to `{}`"
            .format(ctx.author.mention, v_limit, num_msg))
    else:
        await output_channel.send(
            "{} you currently **do not own** any Voice Channel".format(
                ctx.author.mention))


@client.command()
async def goodbye(ctx, user: discord.Member):
    id = request_user_channel(ctx.author.id)
    output_channels = request_template_channel(str(ctx.channel.guild.id))
    output_channel = client.get_channel(int(output_channels[0]))

    if (id != None):
        v_channel = client.get_channel(int(id))
        v_users = v_channel.members

        msg = ""

        for i in v_users:
            if (str(user.id) == str(i.id)):
                await i.move_to(None)
                msg = "{}, {} is sad as he was **removed** from your Voice Channel".format(
                    ctx.author.mention, user.mention)
                break

        if (msg == ""):
            msg = "{} **is not** in your Voice Channel".format(user.mention)

        await output_channel.send(msg)


@client.command()
async def invite(ctx):
    embed = discord.Embed(
        title="__**INVITE**__",
        description=
        "-- -- -- -- --\n[Invite](https://discord.com/oauth2/authorize?client_id=821396921985925131&permissions=63966224&scope=bot) **Caramel Audio** to your server\n-- -- -- -- --",
        color=0xffbb00)
    embed.add_field(
        name="Still Having Problems?",
        value=
        "[Join the Support Server](https://discord.gg/WysSQg2njs)\nor\n[Check the Website](https://example.org)",
        inline=True)
    embed.set_footer(text="Made with ❤️ by Sarwin")
    await ctx.send(embed=embed)


@client.command()
async def vote(ctx):
    embed = discord.Embed(
        title="__**VOTE**__",
        description=
        "-- -- -- -- --\n[Vote](https://discord.com/oauth2/authorize?client_id=821396921985925131&permissions=63966224&scope=bot) **Caramel Audio** to your server\n-- -- -- -- --",
        color=0xffbb00)
    embed.add_field(
        name="Still Having Problems?",
        value=
        "[Join the Support Server](https://discord.gg/WysSQg2njs)\nor\n[Check the Website](https://example.org)",
        inline=True)
    embed.set_footer(text="Made with ❤️ by Sarwin")
    await ctx.send(embed=embed)


'''
@client.command()
async def deafen(ctx, user:discord.Member):
    id = request_user_channel(ctx.author.id)
    output_channels = request_template_channel(str(ctx.channel.guild.id))
    output_channel = client.get_channel(int(output_channels[0]))
    
    if(id != None):
        v_channel = client.get_channel(int(id))
        v_users = v_channel.members

        msg = ""

        for i in v_users:
         if(str(user.id) == str(i.id)):
             await i.edit(deafen=True)
             msg = "{}, {} is sad as he was **deafen**".format(ctx.author.mention, user.mention)
             break

        if(msg == ""):
            msg = "{} **is not** in your Voice Channel".format(user.mention)

        await output_channel.send(msg)

@client.command()
async def mute(ctx, user:discord.Member):
    id = request_user_channel(ctx.author.id)
    output_channels = request_template_channel(str(ctx.channel.guild.id))
    output_channel = client.get_channel(int(output_channels[0]))
    
    if(id != None):
        v_channel = client.get_channel(int(id))
        v_users = v_channel.members

        msg = ""

        for i in v_users:
         if(str(user.id) == str(i.id)):
             await i.edit(mute=True)
             msg = "{}, {} is sad as he was **deafen**".format(ctx.author.mention, user.mention)
             break

        if(msg == ""):
            msg = "{} **is not** in your Voice Channel".format(user.mention)

        await output_channel.send(msg)

@client.command()
async def undeafen(ctx, user:discord.Member):
    id = request_user_channel(ctx.author.id)
    output_channels = request_template_channel(str(ctx.channel.guild.id))
    output_channel = client.get_channel(int(output_channels[0]))
    
    if(id != None):
        v_channel = client.get_channel(int(id))
        v_users = v_channel.members

        msg = ""

        for i in v_users:
         if(str(user.id) == str(i.id)):
             await i.edit(deafen=False)
             msg = "{}, {} is sad as he was **deafen**".format(ctx.author.mention, user.mention)
             break

        if(msg == ""):
            msg = "{} **is not** in your Voice Channel".format(user.mention)

        await output_channel.send(msg)

@client.command()
async def unmute(ctx, user:discord.Member):
    id = request_user_channel(ctx.author.id)
    output_channels = request_template_channel(str(ctx.channel.guild.id))
    output_channel = client.get_channel(int(output_channels[0]))
    
    if(id != None):
        v_channel = client.get_channel(int(id))
        v_users = v_channel.members

        msg = ""

        for i in v_users:
         if(str(user.id) == str(i.id)):
             await i.edit(mute=False)
             msg = "{}, {} is sad as he was **deafen**".format(ctx.author.mention, user.mention)
             break

        if(msg == ""):
            msg = "{} **is not** in your Voice Channel".format(user.mention)

        await output_channel.send(msg)
'''
#check perms
#remove form db


@client.command()
async def help(ctx):
    embed = discord.Embed(
        title="__**HELP MENU**__",
        description=
        "-- -- -- -- --\n**My prefix is [`c.`]**\n-- -- -- -- --\nSet a channel where the bot receives commands and can reply to users\n[`c. output #channel`]\n-- -- -- -- --\nSet a Voice Channel that should be cloned when a user enters it. You can have multiple Channel Template \n[`c. addtemplate`]\n-- -- -- -- --\nReset all settings of this server. __**WARNING USE WITH CAUTION**__ \n[`c.reset CONFIRM`]\n-- -- -- -- --\nGet a list of channels that are considered as a Template Channel\n[`c.templatelist`]\n-- -- -- -- --\nGet a list of customization commands that enables the owner of a Voice Channel to tune the channel to their heart's content\n[`c.cmd`]\n-- -- -- -- --\nGet help - will send you this message\n[`c.help`]\n-- -- -- -- --\nThanks for choosing Caramel Audio\n-- -- -- -- --",
        color=0xffbb00)
    embed.add_field(
        name="Still Having Problems?",
        value=
        "[Join the Support Server](https://discord.gg/WysSQg2njs)\nor\n[Check the Website](https://caramelaudiowebsite.sarwin.repl.co/index.html)",
        inline=True)
    embed.set_footer(text="Made with ❤️ by Sarwin")
    await ctx.send(embed=embed)


@client.command()
async def cmd(ctx):
    embed = discord.Embed(
        title="__**CUSTOMIZATION MENU**__",
        description=
        "-- -- -- -- --\n**My prefix is [`c.`]**\n-- -- -- -- --\nChange the name of your Voice Channel\n[`c.name <name>`]\n-- -- -- -- --\nChange the user limit of your Voice Channel\n[`c.userlimit <number>`]\n-- -- -- -- --\nChange the bitrate of your Voice Channel. If <number> is not within the lower or upper bitrate range of the server it will be set to one of the limits closest to <number>\n[`c.bitrate <number>`]\n-- -- -- -- --\nKick someone from your Voice Channel\n[`c.goodbye @user`]\n-- -- -- -- --\nInvite the bot to your server\n[`c.invite`]\n-- -- -- -- --",
        color=0xffbb00)
    embed.add_field(
        name="Still Having Problems?",
        value=
        "[Join the Support Server](https://discord.gg/WysSQg2njs)\nor\n[Check the Website](https://caramelaudiowebsite.sarwin.repl.co/index.html))",
        inline=True)
    embed.set_footer(text="Made with ❤️ by Sarwin")
    await ctx.send(embed=embed)


@client.event
async def on_command_error(ctx, error):
    if (isinstance(error, commands.MissingPermissions)):
        await ctx.send("**Missing permissions**")
    else:
        if (isinstance(error, commands.MissingRequiredArgument)):
            await ctx.send("**Missing Arguments - Do `c.help` for info**")
        else:
            await ctx.send(error)


keep_alive()
client.run(os.getenv('TOKEN'))
