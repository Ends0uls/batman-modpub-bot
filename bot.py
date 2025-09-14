import os
import discord
import feedparser
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))  # where bot posts updates
CHECK_INTERVAL = 300  # seconds (5 min)

# RSS feeds for Batman games
RSS_FEEDS = {
    "Arkham Knight": "https://mod.pub/batman-arkham-knight/rss",
    "Arkham Asylum": "https://mod.pub/batman-arkham-asylum-game-of-the-year-edition/rss",
    "Arkham Origins": "https://mod.pub/batman-arkham-origins/rss",
    "Arkham City": "https://mod.pub/batman-arkham-city-game-of-the-year-edition/rss",
}

intents = discord.Intents.default()

class ModPubBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.seen_entries = set()

    async def setup_hook(self):
        # Start background task after client is ready
        self.bg_task = asyncio.create_task(self.fetch_and_post())

    async def fetch_and_post(self):
        await self.wait_until_ready()
        channel = self.get_channel(CHANNEL_ID)

        while not self.is_closed():
            for game, url in RSS_FEEDS.items():
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    if entry.link not in self.seen_entries:
                        self.seen_entries.add(entry.link)

                        embed = discord.Embed(
                            title=entry.title,
                            url=entry.link,
                            description=entry.get("summary", "New mod published!"),
                            color=0x2ecc71
                        )
                        embed.set_author(name=game)
                        embed.set_footer(text="Source: mod.pub")

                        await channel.send(embed=embed)
            await asyncio.sleep(CHECK_INTERVAL)

    async def on_ready(self):
        print(f"✅ Logged in as {self.user}")

client = ModPubBot()
client.run(TOKEN)
