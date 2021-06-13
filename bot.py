import requests
import json
import discord
import asyncio
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from discord.ext import commands

token_ = <discord bot token>
api_key = <hypixel api key>
fbUrl = <firebase realtime database url>

cred = credentials.Certificate('firebase-adminsdk.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': fbUrl
})

refo = db.reference('discord')
ref = refo.get()


def getInfo(call):
  r = requests.get(call)
  return r.json()

client = commands.Bot(command_prefix = "!", case_insensitive=True)


@client.event
async def on_ready():
  print("Bot is ready! :)")

@client.command(pass_context=True)
async def verify(ctx):

  try:
    uuid = db.reference('discord').get()[str(ctx.author.id)]
    link = f'https://api.hypixel.net/player?key={api_key}&uuid={uuid}'
    data = getInfo(link)
    try:
      stars = data["player"]["achievements"]["bedwars_level"]
      name = data["player"]["displayname"]
      nick = f"[{stars}⭐] {name}"
      await ctx.author.edit(nick=nick)
      embed=discord.Embed(title="Linked",description="You've already linked with us before, so we were able to automatically link your account. Use !unlink to unlink your account if you want to switch at any time.", color=0x00ff00)
      await ctx.send(embed=embed)
    except:
      embed=discord.Embed(title="Error Checking Hypixel Database", description="You may be sending too many verification requests.", color=0xff0000)
      await ctx.send(embed=embed)
  except:

    embed = discord.Embed(
      title = "Hypixel Verify",
      description = "1. Join Hypixel\n\n2. Right click your player head in your hotbar\n\n3. Left click the social media menu (Twitter icon)\n\n4. Click the Discord icon\n\n5. Type your Discord username and tag in chat (e.g. Pacific#0898).\n\n5. Send your Minecraft Username into this channel",
      color = discord.Color.blue()
    )

    await ctx.send(embed=embed)

    try:
      msg = await client.wait_for('message', timeout=20.0, check=lambda message: message.author == ctx.author)

    except asyncio.TimeoutError:
      embed=discord.Embed(title="Cancelled", description="Did not input a username in time. Type !verify once you have added your Discord to your Hypixel profile.", color=0xff0000)
      await ctx.send(embed=embed)

    else:
      await ctx.send("Checking database...")
      name = msg.content
      link = f'https://api.hypixel.net/player?key={api_key}&name={name}'
      data = getInfo(link)

      status = data["success"]

      if status == False:
        embed=discord.Embed(title="Error Checking Hypixel Database", description=data["cause"], color=0xff0000)
        await ctx.send(embed=embed)

      if status == True:
        try:
          disc = data["player"]["socialMedia"]["links"]["DISCORD"]

          if str(ctx.author) == disc:
            embed=discord.Embed(title="Linked",description="Minecraft/Hypixel account linked.", color=0x00ff00)
            await ctx.send(embed=embed)
            try: 
              stars = data["player"]["achievements"]["bedwars_level"]
              name = data["player"]["displayname"]
              nick = f"[{stars}⭐] {name}"
              await ctx.author.edit(nick=nick)
            except:
              stars = 0
              name = data["player"]["displayname"]
              nick = f"[{stars}⭐] {name}"
              await ctx.author.edit(nick=nick)
            finally:
              try:
                db.reference('discord').update({
                  str(ctx.author.id): str(data["player"]["uuid"])
                })
              except:
                embed=discord.Embed(title="Not Linked", description=f"We were unable to add you to our linked database. Please reverify later. If the issue persists, please contact a staff member.", color=0xff0000)
                await ctx.send(embed=embed)

              
          else:
            embed=discord.Embed(title="Not Linked", description=f"Your Discord {ctx.message.author} does not match the recorded Discord {disc}", color=0xff0000)
            await ctx.send(embed=embed)

        except Exception as e:
          embed=discord.Embed(title="Invalid", description="No Discord linked to Minecraft/Hypixel account OR account does not exist.", color=0xff0000)
          await ctx.send(embed=embed)
          print(e)

@client.command(pass_context=True)
async def update(ctx):
  try:
    uuid = db.reference('discord').get()[str(ctx.author.id)]
    link = f'https://api.hypixel.net/player?key={api_key}&uuid={uuid}'
    data = getInfo(link)
    try: 
      stars = data["player"]["achievements"]["bedwars_level"]
      name = data["player"]["displayname"]
      nick = f"[{stars}⭐] {name}"
      await ctx.author.edit(nick=nick)
    except:
      stars = 0
      name = data["player"]["displayname"]
      nick = f"[{stars}⭐] {name}"
      await ctx.author.edit(nick=nick) 
  except:
    embed=discord.Embed(title="Not Linked", description="You are not in our linked database or you are sending too many requests. Please use !verify.", color=0xff0000)
    await ctx.send(embed=embed)

@client.command(pass_context=True)
async def unlink(ctx):
  try:
    db.reference('discord').child(str(ctx.author.id)).delete()
    embed=discord.Embed(title="Unlinked",description="Minecraft/Hypixel account unlinked.", color=0x00ff00)
    await ctx.send(embed=embed)
    await ctx.author.edit(nick=ctx.message.author.name)
  except Exception as e:
    embed=discord.Embed(title="Not Linked", description="You are not in our linked database. Please use !verify.", color=0xff0000)
    await ctx.send(embed=embed)
    print(e)


client.run(token_)
