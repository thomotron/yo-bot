#!/usr/bin/python3

import discord
from discord.ext import commands
import sqlite3
import requests

DISCORD_BOT_TOKEN = ''
YO_API_TOKEN = ''

bot = commands.Bot(command_prefix='yo ', description='A bot that sends a Yo to a user.')

@bot.event
async def on_ready():
    print('Logged in as {0} ({1})'.format(bot.user.name, bot.user.id))
    print('----------')

@bot.command()
async def yo(ctx):
    await ctx.send("Yo")

@bot.command(pass_context=True)
async def send(ctx, recipient: str):

    if not ctx.message.mentions:

        if not recipient:
            await ctx.send("You didn't mention anyone to send a Yo to.")
            return
        else:
            requests.post("https://api.justyo.co/yo/", data={'api_token': YO_API_TOKEN, 'username': recipient})
            await ctx.send("Sent a Yo to {0}".format(recipient))
            return

    db = sqlite3.connect('users.db')
    dbmod = db.cursor()

    dbmod.execute("CREATE TABLE IF NOT EXISTS users ( id text PRIMARY KEY NOT NULL, yoname NOT NULL )")

    dbmod.execute("SELECT yoname FROM users WHERE id='{0}'".format(ctx.message.mentions[0].id))

    recipient = dbmod.fetchone()

    if not recipient:
        await ctx.send("I couldn't find the Yo username for {0}. Have they registered?".format(ctx.message.mentions[0].mention))
        return

    requests.post("https://api.justyo.co/yo/", data={'api_token': YO_API_TOKEN, 'username': recipient})

    await ctx.send("Sent a Yo to {0}".format(ctx.message.mentions[0].mention))

@bot.command(pass_context=True)
async def register(ctx, yoname: str):

    if not str:
        await ctx.send("You didn't specify a Yo username.")
        return

    db = sqlite3.connect('users.db')
    dbmod = db.cursor()

    dbmod.execute("CREATE TABLE IF NOT EXISTS users ( id text PRIMARY KEY NOT NULL, yoname NOT NULL )")

    dbmod.execute("SELECT id FROM users WHERE id='{0}'".format(ctx.message.author.id)) # <-- Checks for entry

    fetched = dbmod.fetchone()

    print(fetched)
    if fetched is None or str(ctx.message.author.id) not in fetched:
            dbmod.execute("INSERT INTO users (id, yoname) VALUES ('{0}', '{1}')".format(ctx.message.author.id, yoname))
    else:
        dbmod.execute("UPDATE users SET yoname='{1}' WHERE id={0}".format(ctx.message.author.id, yoname))

    db.commit()
    db.close()

    await ctx.send("Registered! All Yo's to {0} will now be sent to \"{1}\"".format(ctx.message.author.mention, yoname))

bot.run(DISCORD_BOT_TOKEN)
