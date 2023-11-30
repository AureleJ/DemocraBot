import settings
import discord
from discord.ext import commands
from discord import ui, app_commands

from discord.ui import Select, View

from datetime import date, datetime, timedelta
import time
import json
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


class Sanctions(Enum):
    Ban = "Ban"
    Kick = "Kick"
    Mute = "Mute"
    Aucune = "None"


@bot.hybrid_command()
async def jugement(ctx, membre: discord.User, sanction: Sanctions, duree, raison):
    embed = discord.Embed(
        description=f"**Jugement de {membre.mention} par {ctx.author.top_role.mention}**",
        colour=0xFF0000,
        timestamp=datetime.now()
    )

    embed.set_author(name=ctx.author.top_role, icon_url=ctx.author.avatar.url)

    embed.add_field(name="Sanction", value=sanction.value, inline=False)
    embed.add_field(name="Raison", value=raison, inline=False)

    embed.set_thumbnail(url=membre.avatar.url)

    # channel = bot.get_channel(1175946419081850902)
    channel = bot.get_channel(1156260066924707920)

    if channel:
        await channel.send(embed=embed)
        await ctx.reply("Le jugement a bien été appliqué", ephemeral=True)
    else:
        await ctx.reply("Le salon de jugement n'a pas été trouvé. Veuillez contacter l'administrateur.")

    if sanction == Sanctions.Kick:
        await kick(ctx, membre, raison)
    elif sanction == Sanctions.Ban:
        await ban(ctx, membre, raison)
    elif sanction == Sanctions.Mute:
        await mute(ctx, membre, duree, raison)


@bot.hybrid_command(name="mute", description="Muter un membre.")
@commands.has_permissions(moderate_members=True)
async def mute(ctx, membre: discord.Member, duree, raison):

    if "s" in duree:
        gettime = duree.strip("s")
        newtime = timedelta(seconds=int(gettime))

    if "m" in duree:
        gettime = duree.strip("m")
        newtime = timedelta(minutes=int(gettime))

    if "h" in duree:
        gettime = duree.strip("h")
        newtime = timedelta(hours=int(gettime))

    if "j" in duree:
        gettime = duree.strip("j")
        newtime = timedelta(days=int(gettime))

    await ctx.reply(f"{membre.mention} a été mute pour `{raison}` pendant `{str(duree)}`", ephemeral=True)
    await membre.send(f"Vous avez été mute sur {ctx.guild.name} pendant {duree} par {ctx.author.top_role} pour: {raison}")
    await membre.edit(timed_out_until=discord.utils.utcnow() + newtime, reason=raison)


@bot.hybrid_command(name="unmute", description="Démuter un membre")
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, membre: discord.Member):

    await ctx.reply(f"{membre.mention} a été démuté`", ephemeral=True)
    await membre.send(f"Vous avez été démute sur {ctx.guild.name}")
    await membre.edit(timed_out_until=None)


@bot.hybrid_command(description="Bannir un membre")
@commands.has_permissions(ban_members=True)
async def ban(ctx, membre: discord.Member, raison):
    # user = await bot.fetch_user(int(membre))

    await ctx.reply(f"{membre.mention} a été ban pour `{raison}`", ephemeral=True)
    await membre.send(f"Vous avez été ban sur {ctx.guild.name} par {ctx.author.top_role} pour: {raison}")
    await ctx.guild.ban(membre)


@bot.hybrid_command(description="Débannir un membre")
@commands.has_permissions(ban_members=True)
async def unban(ctx, membre: discord.Member):
    bannedUsers = await ctx.guild.bans()
    name, discriminator = membre.split("#")

    for ban in bannedUsers:
        user = ban.user

        if (user.name, user.discriminator) == (name, discriminator):
            await ctx.guild.unban(user)
            await ctx.reply(f"{user.mention} a été débani", ephemeral=True)
            await membre.send(f"Vous avez été débani sur {ctx.guild.name}")


@bot.hybrid_command(description="Kick un membre")
@commands.has_permissions(kick_members=True)
async def kick(ctx, membre: discord.Member, raison):
    await ctx.reply(f"{membre.mention} a été kick pour `{raison}`", ephemeral=True)
    await membre.send(f"Vous avez été kick sur {ctx.guild.name} par {ctx.author.top_role} pour: {raison}")
    await membre.kick(reason=raison)

participants = {
    # 328542368037076992: ["Campagne", "Liens", "Description"],
    # 455059373941587988: ["Campagne", "Liens", "Description"],
    # 712954659773480963: ["Campagne", "Liens", "Description"],
    # 1128365951214157834: ["Campagne", "Liens", "Description"],
}


class Candidature(discord.ui.Modal, title='Candidature'):
    name = discord.ui.TextInput(
        label='Nom',
        placeholder='Entrez votre nom ici',
        required=True,
    )

    description = discord.ui.TextInput(
        label='Description personnelle',
        style=discord.TextStyle.long,
        placeholder='Ecrivez votre description ici',
        required=True,
        max_length=300,
    )

    campagne = discord.ui.TextInput(
        label='Votre campagne',
        style=discord.TextStyle.long,
        placeholder='Ecrivez votre campagne ici',
        required=True,
        max_length=300,
    )

    links = discord.ui.TextInput(
        label='Liens a inserer',
        placeholder='Entrez vos liens ici',
        required=False,
    )

    async def on_submit(self, interaction: discord.Interaction):
        participants[interaction.user.id] = [self.campagne.value, self.links.value, self.description.value]
        
        with open("candidatures.json", "w") as f:
            json.dump(participants, f)

        await interaction.response.send_message('Votre candidature a ete transmise', ephemeral=True)

@bot.command()
async def azerty(ctx):
    with open("candidatures.json", "r") as read_file:
        data = json.load(read_file)

    print(data)


class Buttons(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Candidater", style=discord.ButtonStyle.blurple)
    async def blurple_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Candidature())


@bot.command()
async def campagne(ctx):
    await ctx.send("Candidater", view=Buttons())


@bot.command()
async def votes(ctx):
    await ctx.send(embed=discord.Embed(title="Jour des votes", description="Chers membres de la communauté, aujourd'hui est le grand jour des votes", color=0x007bff))

    for participant_id, data in participants.items():
        user = await bot.fetch_user(participant_id)

        embed2 = discord.Embed(
            title=f"Participant {user.global_name}",
            description= data[2],
            colour=0x007bff
        )

        embed2.add_field(name="Campagne", value=data[0], inline=True)
        embed2.add_field(name="Liens importants", value=data[1], inline=True)

        embed2.set_thumbnail(url=user.avatar.url)

        await ctx.send(embed=embed2)

    await votes_selections(ctx, participants)

member_votes = {}


async def votes_selections(ctx, participants):
    options = []

    for participant_id in participants.keys():
        user = await bot.fetch_user(participant_id)

        options.append(discord.SelectOption(label=user.global_name))

    select = Select(placeholder="Votez ici", options=options)

    async def callbacks(interaction):
        if (interaction.user.global_name != select.values[0]):
            await interaction.response.send_message(f"Vous avez voté pour {select.values[0]}", ephemeral=True)
            member_votes[interaction.user.global_name] = select.values[0]
            print(member_votes)
        else:
            await interaction.response.send_message("Vous ne pouvez pas voter pour vous même !", ephemeral=True)

    select.callback = callbacks
    view = View()
    view.add_item(select)
    await ctx.send("Pour qui votez vous ?", view=view)


@bot.command()
async def winner(ctx):
    vote_counts = {}

    for voted_for in member_votes.values():
        if voted_for in vote_counts:
            vote_counts[voted_for] += 1
        else:
            vote_counts[voted_for] = 1

    winner = max(vote_counts, key=vote_counts.get)

    await ctx.send(f"Le gagnant est {winner} avec {vote_counts[winner]} votes!")


@bot.command()
async def del_casier(ctx):
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
async def commissaire(ctx):
    await ctx.send("🚨Attention la police rôde toujours🚨")

bot.run(settings.api_key)
