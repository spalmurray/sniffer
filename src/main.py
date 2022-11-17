import configuration
import data
from sniffer import Sniffer
import discord
from discord import option
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import difflib
import re

intents = discord.Intents.default()
intents.messages = True
bot = discord.Bot(intents=intents)


database = data.Client()
sniffer = Sniffer()


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.slash_command(description="Add a url for me to sniff")
@option("url", description="The url you want me to sniff")
@option("interval", description="How frequently you want me to sniff it", choices=["monthly", "weekly", "daily", "hourly", "minutely"])
async def add_url(
    ctx: discord.ApplicationContext,
    url: str,
    interval: str,
):
    smell = sniffer.sniff(url)
    if not smell:
        await ctx.respond("Please make sure you've entered a valid url.")
        return

    database.add_url(
        url, interval, smell, ctx.guild_id, ctx.channel_id, ctx.author.id
    )

    await ctx.respond(
        f"Gotcha. I'll give {url} a {interval} sniff."
    )

@bot.slash_command(description="List urls registered in this channel")
async def list_channel_urls(ctx: discord.ApplicationContext):
    urls = database.list_channel_urls(ctx.channel_id)
    
    if not urls:
        await ctx.respond("There are no urls associated with this channel.")
        return
    
    response = ""
    for url in urls:
        user = await bot.fetch_user(url["user"])
        response += f'Sniffing {url["url"]} {url["interval"]} for {user.name}\n(id: {url["_id"]})\n\n'
    await ctx.respond(response)

@bot.slash_command(description="List urls registered in this server")
async def list_server_urls(ctx: discord.ApplicationContext):
    urls = database.list_guild_urls(ctx.guild_id)
    
    if not urls:
        await ctx.respond("There are no urls associated with this server.")
        return
    
    response = ""
    for url in urls:
        user = await bot.fetch_user(url["user"])
        response += f'Sniffing {url["url"]} {url["interval"]} for {user.name}\n(id: {url["_id"]})\n\n'
    await ctx.respond(response)

@bot.slash_command(description="Delete a url by its id. Find id with /list_channel_urls")
@option("id", description="The id of the url to delete")
async def delete_url(ctx: discord.ApplicationContext, id: str):
    if not database.delete_url(id, ctx.guild_id):
        await ctx.respond(f"Sorry! I'm not sniffing any urls with that id ({id}) on this server.")
    else:
        await ctx.respond("Okay. I'll no longer sniff that url.")

# Scheduling

async def stinky_alert(url: str, interval: str, channel: int, user: int, diff):
    clean_interval = "day" if interval == "daily" else interval[:-2]
    user = await bot.fetch_user(user)
    message = f'{user.mention}, {url} smells differently this {clean_interval}! Here is the diff:\n```'
    diff_len = 0
    for line in diff:
        if diff_len + len(line) >= 1800:
            break
        message += line 
        diff_len += len(line)
    message += '```'
    await bot.get_channel(channel).send(message)

async def down_alert(url: str, interval: str, channel: int, user: int):
    clean_interval = "day" if interval == "daily" else interval[:-2]
    user = await bot.fetch_user(user)
    message = f'{user.mention}, {url} appears to be down this {clean_interval}!'
    await bot.get_channel(channel).send(message)

async def up_alert(url: str, interval: str, channel: int, user: int):
    clean_interval = "day" if interval == "daily" else interval[:-2]
    user = await bot.fetch_user(user)
    message = f'{user.mention}, {url} appears to be back up this {clean_interval}!'
    await bot.get_channel(channel).send(message)

async def go_sniffing(interval: str):
    urls = database.list_interval_matches(interval)
    for url in urls:
        smell = sniffer.sniff(url["url"])
        if not smell and not url["is_down"]:
            database.set_is_down(url["_id"], True)
            await down_alert(url["url"], url["interval"], url["channel"], url["user"])
            continue
        elif not smell:
            continue
        elif url["is_down"]:
            database.set_is_down(url["_id"], False)
            await up_alert(url["url"], url["interval"], url["channel"], url["user"])

        if smell != url["previous_data"]:
            diff = difflib.unified_diff(re.split('(\n)', url["previous_data"]), re.split('(\n)', smell), fromfile="old", tofile="new")
            database.update_data(url["_id"], smell)
            await stinky_alert(url["url"], url["interval"], url["channel"], url["user"], diff)

scheduler = AsyncIOScheduler()
scheduler.add_job(go_sniffing, 'cron', second=0, args=["minutely"])
scheduler.add_job(go_sniffing, 'cron', minute=0, args=["hourly"])
scheduler.add_job(go_sniffing, 'cron', hour=0, args=["daily"])
scheduler.add_job(go_sniffing, 'cron', day_of_week=0, args=["weekly"])
scheduler.add_job(go_sniffing, 'cron', day=1, args=["monthly"])
scheduler.start()

database.run_migration()
print("Starting sniffer")
config = configuration.Config()
bot.run(config.token)