import discord
from discord.ext import commands
import logging
import asyncio
from discord import app_commands
import random

# Configure logging
logger = logging.getLogger("main.py")
logging.basicConfig(level=logging.INFO)

class PingUser(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        logger.info("PingUser cog initialized")
    @app_commands.command(name='ping', description='Send an @ message to the selected user')
    @app_commands.describe(user='The user to ping')
    async def ping(self, interaction: discord.Interaction, user: discord.Member):
        allowed_users = self.config["allowed_users"]
        logger.info(f"Allowed users: {allowed_users}")
        logger.info(f"User ID: {interaction.user.id}")

        if interaction.user.id not in allowed_users:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return
        
        await asyncio.sleep(1)
        logger.info(f"Received ping command for user {user.display_name}.")
        await interaction.response.send_message(f"Making {user.name} go mad.", ephemeral=True)
        num_pings = random.randint(1, 10)
        for _ in range(num_pings):
            await interaction.channel.send(f"{user.mention}")
            await interaction.channel.purge(limit=1)
            await asyncio.sleep(0.5)

