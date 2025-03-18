import discord
from discord.ext import commands
import asyncio
import logging

# Configure logging
logger = logging.getLogger("app.py")


class WakeUp(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.voice_channels = []
        self.user_to_move = None
        self.cycles = 0
        # self.move_user.start()
        logger.info("WakeUp cog initialized")

    @discord.app_commands.command(
        name="wake", description="Move a user between voice channels"
    )
    @discord.app_commands.describe(
        user="The user to move",
        cycles="Max: 4. Number of cycles to move the user through channels",
    )
    async def wake(
        self, interaction: discord.Interaction, user: discord.Member, cycles: int
    ):
        if cycles > 4:
            await interaction.response.send_message(
                "The maximum number of cycles is 4.", ephemeral=True
            )
            return

        allowed_users = self.config["allowed_users"]
        logger.info(f"Allowed users: {allowed_users}")
        logger.info(f"User ID: {interaction.user.id}")

        if interaction.user.id not in allowed_users:
            await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )
            return

        guild = interaction.guild
        self.voice_channels = [
            channel
            for channel in guild.voice_channels
            if isinstance(channel, discord.VoiceChannel)
        ]
        channel_ids = [channel.id for channel in self.voice_channels]
        back = False
        self.user_to_move = user
        original_channel = user.voice.channel
        current_cycle = 0

        logger.info(
            f"Received wake command for user {user.display_name} with {cycles} cycles."
        )
        await interaction.response.send_message(
            f"Starting to move {user.display_name} through channels for {cycles} cycles.",
            ephemeral=True,
        )

        while current_cycle < cycles and not back:
            for channel_id in channel_ids:
                channel = self.bot.get_channel(channel_id)
                logger.info(f"Moving {user.display_name} to channel {channel.name}.")
                await user.move_to(channel)
                await asyncio.sleep(2.5)
                current_channel = user.voice.channel
                if current_channel.id != channel_id:
                    logger.info(
                        f"{user.display_name} is no longer in channel {channel_id}. Stopping the cycle."
                    )
                    back = True
                    break
            current_cycle += 1
            logger.info(f"Current cycle: {current_cycle}")

        logger.info(f"Finished moving {user.display_name} through channels.")
        await interaction.followup.send(
            f"Finished moving {user.display_name} through channels.", ephemeral=True
        )
        await user.move_to(original_channel)
