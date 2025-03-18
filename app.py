import discord
import json
import os
import asyncio
import logging
from discord.ext import commands
from cogs.wake import WakeUp
from cogs.ping import PingUser
from cogs.purge import PurgeMessages

# Ensure logs directory exists
log_dir = "/logs"
os.makedirs(log_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    handlers=[logging.FileHandler(f"{log_dir}/bot.log", encoding="utf-8")],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.info("Logging initialized successfully.")

# Load bot tokens
currentDir = os.path.dirname(os.path.abspath(__file__))
tokens_file = os.path.join(currentDir, "tokens.json")
with open(tokens_file, "r") as file:
    configTokens = json.load(file)


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
        self.config = configTokens
        self.cogsToLoad = {
            "wake": WakeUp,
            "ping": PingUser,
            "purge": PurgeMessages,
        }

    async def on_ready(self):
        logging.info(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.change_presence(activity=discord.Game(name="v1.0"))

        # Load Cogs
        for cogName, cogClass in self.cogsToLoad.items():
            try:
                if cogName not in self.cogs:
                    await self.add_cog(cogClass(self, self.config))
                    logging.info(f"Successfully loaded cog: {cogName}")
            except Exception as e:
                logging.exception(f"Failed to load cog: {cogName} | ERROR: {e}")

        # Sync application commands
        try:
            await self.tree.sync()
            logging.info("Slash commands synced.")
        except Exception as e:
            logging.exception(f"Error syncing commands: {e}")


if __name__ == "__main__":
    bot = MyBot()

    async def shutdown():
        logging.info("Shutting down bot...")
        await bot.close()

    try:
        bot.run(configTokens["discord_token"])
    except KeyboardInterrupt:
        logging.info("Ctrl+C detected. Shutting down gracefully...")
        asyncio.run(shutdown())
