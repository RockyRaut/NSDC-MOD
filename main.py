import discord
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

warns = {}  # Store user warnings temporarily (you can extend to use JSON or DB)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Moderation Bot is online as {bot.user}")


@bot.tree.command(name="kick", description="Kick a member from the server.")
@app_commands.describe(user="User to kick", reason="Reason for kicking")
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
    await user.kick(reason=reason)
    await interaction.response.send_message(f"👢 Kicked {user.mention} for: {reason}")


@bot.tree.command(name="ban", description="Ban a member from the server.")
@app_commands.describe(user="User to ban", reason="Reason for banning")
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
    await user.ban(reason=reason)
    await interaction.response.send_message(f"🔨 Banned {user.mention} for: {reason}")


@bot.tree.command(name="unban", description="Unban a user by name#discriminator")
@app_commands.describe(username="Exact username#1234 of banned user")
async def unban(interaction: discord.Interaction, username: str):
    banned_users = await interaction.guild.bans()
    name, discriminator = username.split('#')
    for ban_entry in banned_users:
        user = ban_entry.user
        if user.name == name and user.discriminator == discriminator:
            await interaction.guild.unban(user)
            await interaction.response.send_message(f"🛡️ Unbanned {user}")
            return
    await interaction.response.send_message("❌ User not found in ban list.")


@bot.tree.command(name="mute", description="Mute a member (timeout)")
@app_commands.describe(user="User to mute", duration="Duration in seconds")
async def mute(interaction: discord.Interaction, user: discord.Member, duration: int):
    await user.timeout(discord.utils.utcnow() + discord.timedelta(seconds=duration))
    await interaction.response.send_message(f"🔇 Muted {user.mention} for {duration} seconds.")


@bot.tree.command(name="unmute", description="Remove timeout from a member")
@app_commands.describe(user="User to unmute")
async def unmute(interaction: discord.Interaction, user: discord.Member):
    await user.timeout(None)
    await interaction.response.send_message(f"🔊 Unmuted {user.mention}.")


@bot.tree.command(name="clear", description="Delete messages in a channel")
@app_commands.describe(amount="Number of messages to delete")
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 Deleted {amount} messages.", ephemeral=True)


@bot.tree.command(name="slowmode", description="Set slowmode delay in a channel")
@app_commands.describe(seconds="Delay in seconds")
async def slowmode(interaction: discord.Interaction, seconds: int):
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f"🐢 Slowmode set to {seconds} seconds.")


@bot.tree.command(name="lock", description="Lock the current channel")
async def lock(interaction: discord.Interaction):
    overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = False
    await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message("🔒 Channel locked.")


@bot.tree.command(name="unlock", description="Unlock the current channel")
async def unlock(interaction: discord.Interaction):
    overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = True
    await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message("🔓 Channel unlocked.")


@bot.tree.command(name="warn", description="Warn a member")
@app_commands.describe(user="User to warn", reason="Reason for warning")
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
    if user.id not in warns:
        warns[user.id] = []
    warns[user.id].append(reason)
    await interaction.response.send_message(f"⚠️ Warned {user.mention} for: {reason}")


@bot.tree.command(name="warnings", description="Show a user's warnings")
@app_commands.describe(user="User to check")
async def warnings(interaction: discord.Interaction, user: discord.Member):
    user_warns = warns.get(user.id, [])
    if not user_warns:
        await interaction.response.send_message(f"{user.mention} has no warnings.")
    else:
        msg = "\n".join(f"{i+1}. {w}" for i, w in enumerate(user_warns))
        await interaction.response.send_message(f"⚠️ Warnings for {user.mention}:\n{msg}")
import os        
bot.run(os.getenv("DISCORD_TOKEN"))
