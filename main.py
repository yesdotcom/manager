import discord, json, os, asyncio
import logging
from discord.ext import commands
from cogs.wake import WakeUp
from cogs.ping import PingUser
from cogs.purge import PurgeMessages

# Configure logging
print("Loading logging...")
logging.basicConfig(
    level=logging.INFO,  # Log level (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log message format
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),  # Log to a file
        logging.StreamHandler()  # Log to the console
    ]
)

currentDir = os.path.dirname(os.path.abspath(__file__))
with open(file=f"{os.path.join(currentDir, 'tokens.json')}", mode="r") as tokensFile:
    configTokens = json.load(tokensFile)

class MyBot(commands.Bot):
    
    logging = logging.getLogger('main.py')
    def __init__(self):
        self.bot = self
        self.config = configTokens
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.all()
        )
        self.cogsToLoad = {
            'wake': WakeUp, # Wake up service
            'ping': PingUser, # Ping service
            'purge': PurgeMessages # Purge service
        }

    async def on_ready(self):
        await bot.change_presence(activity=discord.Game(name="v1.0"))
        user = await self.fetch_user(476047124694433822)
        #await user.send("Bot is now online!")
        # Load Cogs
        for cogName, cogClass in self.cogsToLoad.items():
            try:
                if cogName in self.cogs:
                    logging.info(f"{cogName} already loaded.")
                    continue  # Skip loading this cog if it's already loaded
                if cogName == 'wake':
                    await bot.add_cog(cogClass(bot, self.config))
                if cogName == 'ping':
                    await bot.add_cog(cogClass(bot, self.config))
                if cogName == 'purge':
                    await bot.add_cog(cogClass(bot, self.config))

                logging.info(f"Successfully loaded cog: {cogName}")
            except Exception as e:
                logging.exception(f"Failed to load cog: {cogName} | ERROR: {e}")
                print(f"Failed to load cog {cogName}: {e}")

        # Sync application commands
        try:
            await self.tree.sync()
            logging.info("Slash commands synced.")
        except Exception as e:
            logging.exception(f"Error syncing commands: {e}")

if __name__ == "__main__":
    bot = MyBot()
    async def shutdown(bot):
        await bot.close()
    try:
        bot.run(configTokens['discord_token'])
    except KeyboardInterrupt:
        logging.info("\nCtrl+C detected. Shutting down gracefully...")
        asyncio.run(shutdown(bot))
