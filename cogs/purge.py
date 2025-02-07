import discord
from discord.ext import commands
import logging
import asyncio, discord.ui
from discord import app_commands


# Configure logging
logger = logging.getLogger("main.py")
logging.basicConfig(level=logging.INFO)

class PurgeMessages(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        logger.info("PurgeMessages cog initialized")

    @app_commands.command(name='purge', description='Purge a specified number of messages')
    @app_commands.describe(amount='The number of messages to purge')
    async def purge(self, interaction: discord.Interaction, amount: int):
        allowed_users = self.config["allowed_users"]
        logger.info(f"Allowed users: {allowed_users}")
        logger.info(f"User ID: {interaction.user.id}")

        if interaction.user.id not in allowed_users:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return
        
        logger.info(f"Received purge command to delete {amount} messages from user {interaction.user.name} (ID: {interaction.user.id}).")
        await interaction.response.send_message(f"Purging {amount} messages...", ephemeral=True)

        class PurgeNextButton(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.next_button = discord.ui.Button(label="Purge next message", style=discord.ButtonStyle.primary)
                self.next_button.callback = self.next_button_callback
                self.add_item(self.next_button)

            async def next_button_callback(self, interaction: discord.Interaction):
                logger.info(f"Next button clicked by user {interaction.user.name} (ID: {interaction.user.id}).")
                deleted = await interaction.channel.purge(limit=1)
                if len(deleted) == 0:
                    await interaction.response.send_message("There are no more messages left.", ephemeral=True)
                    return
                logger.info(f"Deleted {len(deleted)} message(s) after next button click.")
                await interaction.response.send_message("done...", ephemeral=True)
                await interaction.delete_original_response()
        await asyncio.sleep(1)
        await interaction.delete_original_response()

        view = PurgeNextButton()
        try:
            deleted = await interaction.channel.purge(limit=amount)
            logger.info(f"Deleted {len(deleted)} messages.")
            await interaction.followup.send(
                f"Done.",
                view=view,
                ephemeral=True,
            )
        except discord.Forbidden:
            logger.error("Bot does not have permission to delete messages.")
            await interaction.followup.send("I do not have permission to delete other's messages, enable **Manage Messages** in this channel's permissions.", ephemeral=True)
    

