import discord
import settings
from discord.ext import commands
from discord import app_commands
from datetime import date, datetime
import time
import json
from typing import List
from enum import Enum

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

bot = commands.Bot(command_prefix='!', intents=intents)

intents.message_content = True
intents.guilds = True
intents.members = True


@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)


@bot.hybrid_command()
async def voltaire(ctx, *, message):
    await ctx.send(f"{message} : https://www.projet-voltaire.fr/")


@bot.hybrid_command()
async def train(ctx, *, member: discord.Member = None):
    train = 'petit'

    if member.id == 410111790970568705:
        train = 'très grand'

    await ctx.send(f"Effectivement d'après le théorème des trains {member.mention} a un {train} train !!! 🚂🚂")


@bot.hybrid_command()
async def aurele(ctx):
    await ctx.send("c'est le plus bo")


@bot.hybrid_command(name="ping", description="Make ping test")
async def ping(ctx, message):
    if message == None:
        await ctx.send("Il manque un argument")
    await ctx.send('pong')


with open('lois.json', 'r', encoding='utf-8') as json_file:
    laws_data = json.load(json_file)


@bot.hybrid_command()
async def lois(ctx, loi_id: int = None):
    if loi_id is None:
        await ctx.send("Veuillez preciser l'article souhaité (1 -> 7)")
    else:
        law = next(
            (article for article in laws_data['articles'] if article['id'] == loi_id), None)
        if law:
            await ctx.send(f"**__{law['title']} :__**\n{law['content']}")
        else:
            await ctx.send("La loi n'existe pas.")


@bot.hybrid_command()
async def commisaire(ctx):
    await ctx.send("🚨Attention la police rôde toujours🚨")


class Sanctions(Enum):
    Ban = "Ban"
    Kick = "Kick"
    Mute = "Mute"


@bot.hybrid_command()
async def jugement(ctx, membre: discord.Member = None, sanction: Sanctions = None, raison: str = None):
    if membre is None:
        await ctx.send("Veuillez mentionner un membre.")
        return

    if sanction is None:
        await ctx.send("Veuillez spécifier une sanction.")
        return

    if raison is None:
        await ctx.send("Veuillez spécifier une raison.")
        return

    if sanction == Sanctions.Kick:
        await kick(ctx, membre, raison)
    elif sanction == Sanctions.Ban:
        await ban(ctx, membre, raison)
    elif sanction == Sanctions.Mute:
        await mute(ctx, membre, raison)

    embed = discord.Embed(
        description=f"**Jugement de {membre.mention} par {ctx.author.top_role.mention}**",
        colour=0xFF0000,
        timestamp=datetime.now()
    )

    embed.set_author(name=ctx.author.top_role, icon_url=ctx.author.avatar.url)

    embed.add_field(name="Sanction", value=sanction.value, inline=False)
    embed.add_field(name="Raison", value=raison, inline=False)

    embed.set_thumbnail(url=membre.avatar.url)

    channel = bot.get_channel(1175946419081850902)
    if channel:
        await channel.send(embed=embed)
        await ctx.reply("Le jugement a bien été appliqué", ephemeral=True)
    else:
        await ctx.reply("Le salon de jugement n'a pas été trouvé. Veuillez contacter l'administrateur.")


@bot.hybrid_command(description="Muter un membre.")
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, raison: str = None):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        if ctx.guild.me.guild_permissions.manage_roles:
            mutedRole = await guild.create_role(name="Muted")

            for channel in guild.channels:
                await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, view_channel=True, read_messages=True)

    if mutedRole not in member.roles:
        await member.add_roles(mutedRole, reason=raison)
        await ctx.reply(f"{member.mention} a été mute pour : {raison}", ephemeral=True)
        await member.send(f"Vous avez été mute sur {guild.name} par {ctx.author.top_role} pour: {raison}")
    else:
        await ctx.reply(f"{member.mention} a déjà été mute.", ephemeral=True)


@bot.hybrid_command(description="Démuter un membre")
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member):
    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")

    if mutedRole in member.roles:
        await member.remove_roles(mutedRole)
        await ctx.reply(f"{member.mention} a été démuté")
        await member.send(f"Vous avez été démute sur {ctx.guild.name}")
    else:
        await ctx.send(f"{member.mention} n'est pas mute")


@bot.command(description="Bannir un membre")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, raison: str = None):
    await member.send(f"Vous avez été ban de {ctx.guild.name} par {ctx.author.top_role} pour: {raison}")
    await member.ban(reason=raison)
    await ctx.send(f"{member} a été banni")


@bot.command(description="Kick un membre")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, raison: str = None):
    await member.send(f"Vous avez été ban de {ctx.guild.name} par {ctx.author.top_role} pour: {raison}")
    await member.kick(reason=raison)
    await ctx.send(f"{member} a été kick")


@bot.command(description="débanir un membre")
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    bannedUsers = await ctx.guild.bans()
    name, discriminator = member.split("#")

    for ban in bannedUsers:
        user = ban.user

        if (user.name, user.discriminator) == (name, discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f"{user.mention} a été débani")
            return


@bot.hybrid_command()
async def votes(ctx, duree: int, participants: str):
    await ctx.send(embed=discord.Embed(title="Jour des votes", description="Chers membres de la communauté, aujourd'hui est le grand jour des votes", color=0x007bff))

    participants = {
        410111790970568705: ["Campagne", "Liens"],
        328542368037076992: ["Campagne", "Liens"],
        455059373941587988: ["Campagne", "Liens"],
        712954659773480963: ["Campagne", "Liens"]
    }

    for participant_id, data in participants.items():
        user = await bot.fetch_user(participant_id)

        embed2 = discord.Embed(
            title=f"Participant {user.global_name}",
            description="Description personnelle",
            colour=0x007bff
        )

        embed2.add_field(name="Campagne", value=data[0], inline=True)
        embed2.add_field(name="Liens importants", value=data[1], inline=True)

        embed2.set_thumbnail(url=user.avatar.url)

        await ctx.send(embed=embed2)
        await ctx.send(view=MyView(user.name))

vote_counts = {}
member_votes = {}


class MyView(discord.ui.View):
    def __init__(self, participant_name: str):
        super().__init__()
        self.participant_name = participant_name

    @discord.ui.button(label="Vote", style=discord.ButtonStyle.green)
    async def button_callback(self, interaction: discord.Integration, button: discord.ui.Button):
        vote_counts[self.participant_name] = vote_counts.get(
            self.participant_name, 0) + 1
        member_votes[interaction.user.name] = self.participant_name
        print(
            f"Vote pour {self.participant_name}. Nombre total de votes : {vote_counts}")
        print(member_votes)
        await interaction.response.send_message(f"Vous avez voté pour {self.participant_name}", ephemeral=True)


@bot.command()
async def result(ctx):
    if member_votes != {}:
        for participant, vote in vote_counts.items():
            winner = participant

            if vote >= vote_counts[winner]:
                winner = "Le vainqueur est : " + participant
    else:
        winner = "Le vote n'est pas encore terminé"
    await ctx.send(winner)


@bot.hybrid_command()
async def avatar(ctx, *,  member: discord.Member = None):
    userAvatarUrl = member.avatar.url
    await ctx.send(userAvatarUrl)


@bot.command()
async def dele(ctx):
    messages = [message async for message in ctx.channel.history(limit=123, oldest_first=True)]
    # print(messages[0].content)
    posted = messages[0].created_at.date().strftime('%d')
    today = date.today().strftime('%d')
    if int(today) - int(posted) >= 15:
        await messages[0].delete()
        botMessage = await ctx.reply("Le dernier message a ete suprimmé", ephemeral=True)
        time.sleep(2)
        await botMessage.delete()
        await ctx.message.delete()
    else:
        botMessage = await ctx.reply("La suppression des messages est a jour", ephemeral=True)
        time.sleep(2)
        await botMessage.delete()
        await ctx.message.delete()
bot.run(settings.api_key)
