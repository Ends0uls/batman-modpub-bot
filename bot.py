import os
import discord
import feedparser
import asyncio
from datetime import datetime

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))  # channel where bot posts
CHECK_INTERVAL = 120  # seconds (2 min)

# RSS feeds for Batman games
RSS_FEEDS = {
    "Batman: Arkham Knight": "https://mod.pub/batman-arkham-knight/rss",
    "Batman: Arkham Asylum GOTY": "https://mod.pub/batman-arkham-asylum-game-of-the-year-edition/rss",
    "Batman: Arkham Origins": "https://mod.pub/batman-arkham-origins/rss",
    "Batman: Arkham City GOTY": "https://mod.pub/batman-arkham-city-game-of-the-year-edition/rss",
}

intents = discord.Intents.default()

class ModPubBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.seen_entries = set()

    async def setup_hook(self):
        self.bg_task = asyncio.create_task(self.fetch_and_post())

    async def fetch_and_post(self):
        await self.wait_until_ready()
        channel = self.get_channel(CHANNEL_ID)

        while not self.is_closed():
            print("🔄 Checking mod.pub feeds...")
            for game, url in RSS_FEEDS.items():
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    if entry.link not in self.seen_entries:
                        self.seen_entries.add(entry.link)

                        # Build a Nexus Mods–style embed
                        embed = discord.Embed(
                            title=entry.title,
                            url=entry.link,
                            description=entry.get("summary", "New mod released!"),
                            color=0x3498db,
                            timestamp=datetime.utcnow()
                        )
                        embed.set_author(name=game, icon_url="https://mod.pub/static/img/favicon.png")
                        embed.set_footer(text="Source: mod.pub")

                        # Try to include image/thumbnail if available
                        if "media_thumbnail" in entry and entry.media_thumbnail:
                            embed.set_thumbnail(url=entry.media_thumbnail[0]["url"])
                        elif "media_content" in entry and entry.media_content:
                            embed.set_thumbnail(url=entry.media_content[0]["url"])

                        await channel.send(embed=embed)
                        print(f"✅ Posted new mod: {entry.title} ({game})")
            await asyncio.sleep(CHECK_INTERVAL)

    async def on_ready(self):
        print(f"✅ Logged in as {self.user}")

client = ModPubBot()
client.run(TOKEN)
