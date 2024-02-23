import settings
import discord
from discord.ext import commands
from discord import app_commands

from discord.ui import Select, View, Button, TextInput, Modal

from datetime import date, datetime, timedelta
import time
import json
from enum import Enum


intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
activity = discord.Activity(type=discord.ActivityType.watching, name="si Maxence est sage...")

bot = commands.Bot(command_prefix="!", intents=intents,
                   activity=activity, status=discord.Status.online)

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


# @bot.event
# async def on_message(message):
#     if 'quoi' in message.content.lower():
#         emojis = ["🇫", "🇪", "🇺", "🇷"]
#         for emoji in emojis:
#             await message.add_reaction(emoji)


class Sanctions(Enum):
    Ban = "Ban"
    Kick = "Kick"
    Mute = "Mute"
    Aucune = "None"


@bot.hybrid_command()
async def jugement(ctx, membre: discord.User, sanction: Sanctions, duree, raison):
    if (ctx.author.top_role.position < membre.top_role.position):
        await ctx.reply("Vous ne pouvez pas appliquer un jugement sur ce membre", ephemeral=True)
        return False
    if (membre.id == ctx.author.id):
        await ctx.reply("Mais tu peux pas te faire un jugement a toi meme troubadour va...", ephemeral=True)
        return False

    if sanction == Sanctions.Kick:
        await kick(ctx, membre, raison)
    elif sanction == Sanctions.Ban:
        await ban(ctx, membre, raison)
    elif sanction == Sanctions.Mute:
        await mute(ctx, membre, duree, raison)

    embed = discord.Embed(
        description=f"**Jugement de {membre.mention} par {ctx.author.top_role.mention}**",
        colour=0xFF0000,
        timestamp=datetime.now()
    )

    embed.set_author(name=ctx.author.top_role, icon_url=ctx.author.avatar.url)

    embed.add_field(name="Sanction", value=sanction.value, inline=False)
    embed.add_field(name="Durée", value=duree, inline=False)
    embed.add_field(name="Raison", value=raison, inline=False)

    embed.set_thumbnail(url=membre.avatar.url)

    channel = bot.get_channel(1156260066924707920)

    if channel:
        await channel.send(embed=embed)
        await ctx.reply("Le jugement a bien été appliqué", ephemeral=True)
    else:
        await ctx.reply("Le salon de jugement n'a pas été trouvé. Veuillez contacter l'administrateur.")

@bot.hybrid_command(name="mute", description="Muter un membre.")
@commands.has_permissions(moderate_members=True)
async def mute(ctx, membre: discord.Member, duree, raison):

    if "s" in duree or "S" in duree:
        gettime = duree.strip("s")
        newtime = timedelta(seconds=int(gettime))

    if "m" in duree or "M" in duree:
        gettime = duree.strip("m")
        newtime = timedelta(minutes=int(gettime))

    if "h" in duree or "G" in duree:
        gettime = duree.strip("h")
        newtime = timedelta(hours=int(gettime))

    if "j" in duree or "J" in duree:
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


def get_json_data(path):
    with open(path, "r", encoding="utf-8") as file_name:
        data = json.load(file_name)
    return data


def save_json_data(path, data):
    with open(path, "w", encoding="utf-8") as file_name:
        json.dump(data, file_name, indent=4)


@bot.hybrid_command()
async def peine(ctx, membre: discord.User, peine):

    if (ctx.author.top_role.position < membre.top_role.position):
        await ctx.reply("Vous ne pouvez pas appliquer une peine sur ce membre", ephemeral=True)
        return False
    if (membre.id == ctx.author.id):
        await ctx.reply("Mais tu peux pas te faire une peine à toi même troubadour va...", ephemeral=True)
        return False

    embed = discord.Embed(
        description=f"**Peine de {membre.mention} par {ctx.author.top_role.mention}**",
        colour=0x00FF00,
        timestamp=datetime.now()
    )
    embed.set_author(name=ctx.author.top_role, icon_url=ctx.author.avatar.url)
    embed.add_field(name="Peine", value=peine, inline=False)
    embed.set_thumbnail(url=membre.avatar.url)

    embed2 = discord.Embed(
        description=f"**Valider l'inculpation :**",
        colour=0x00FF00,
    )    
    
    embed3 = discord.Embed(
        description=f"**Valider le réquisitoire :**",
        colour=0x00FF00,
    )

    view1 = View(timeout=None)
    oui1 = Button(label="Oui", style=discord.ButtonStyle.green, custom_id="oui1")
    non1 = Button(label="Non", style=discord.ButtonStyle.red, custom_id="non1")    
    
    view2 = View(timeout=None)
    oui2 = Button(label="Oui", style=discord.ButtonStyle.green, custom_id="oui2")
    non2 = Button(label="Non", style=discord.ButtonStyle.red, custom_id="non2")

    async def vote_callback(interaction: discord.Interaction, vote_type: str):
        if vote_type == "oui1":
            await interaction.response.send_message(f"Vous avez voté oui", ephemeral=True)
        elif vote_type == "non1":
            await interaction.response.send_message(f"Vous avez voté non", ephemeral=True)
        elif vote_type == "oui2":
            await interaction.response.send_message(f"Vous avez voté oui", ephemeral=True)
        elif vote_type == "non2":
            await interaction.response.send_message(f"Vous avez voté non", ephemeral=True)

        try:
            file_data = get_json_data("peines.json")
        except json.decoder.JSONDecodeError:
            file_data = {}

        if str(interaction.user.id) not in file_data:
            file_data[str(interaction.user.id)] = {}
        file_data[str(interaction.user.id)][vote_type] = membre.id
        save_json_data("peines.json", file_data)

    oui1.callback = lambda inter: vote_callback(inter, "oui1")
    non1.callback = lambda inter: vote_callback(inter, "non1")
    view1.add_item(item=oui1)
    view1.add_item(item=non1)

    oui2.callback = lambda inter: vote_callback(inter, "oui2")
    non2.callback = lambda inter: vote_callback(inter, "non2")
    view2.add_item(item=oui2)
    view2.add_item(item=non2)

    await ctx.send(embed=embed)
    await ctx.channel.send(embed=embed2, view=view1)
    await ctx.channel.send(embed=embed3, view=view2)
    await ctx.reply("La peine a bien été appliquée", ephemeral=True)



class Candidature(Modal, title='Candidature'):
    description_personnelle = TextInput(
        label='Description personnelle',
        style=discord.TextStyle.long,
        placeholder='Ecrivez votre description ici',
        required=True,
        max_length=1024,
    )

    campagne = TextInput(
        label='Votre campagne',
        style=discord.TextStyle.long,
        placeholder='Ecrivez votre campagne ici',
        required=True,
        max_length=1024,
    )

    links = TextInput(
        label='Liens a inserer',
        style=discord.TextStyle.short,
        placeholder='Entrez vos liens ici',
        required=False,
    )

    async def on_submit(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        try:
            file_data = get_json_data("candidatures.json")
        except json.decoder.JSONDecodeError:
            file_data = {}

        file_data[user_id] = [self.description_personnelle.value,
                              self.campagne.value, self.links.value]

        save_json_data("candidatures.json", file_data)

        await interaction.response.send_message('Votre candidature a été transmise', ephemeral=True)


@bot.command()
async def candidature(ctx):
    view = View(timeout=None)
    buttonCandidature = Button(label="Candidater", style=discord.ButtonStyle.blurple, custom_id="candidate", emoji="🏛️")

    async def button_callback(interaction: discord.Interaction):
        await interaction.response.send_modal(Candidature())

    buttonCandidature.callback = button_callback
    view.add_item(item=buttonCandidature)
    await ctx.send(view=view)


@bot.command()
async def candidature_delete(ctx):
    file_data = get_json_data("candidatures.json")
    user_id = str(ctx.author.id)

    if str(user_id) in file_data:
        del file_data[str(user_id)]
        save_json_data("candidatures.json", file_data)
        await ctx.reply("Votre candidature a été supprimée avec succès.", ephemeral=True)
    else:
        await ctx.reply("Aucune candidature trouvée à supprimer.", ephemeral=True)


""" @bot.command()
async def candidature_edit(ctx):
    view = View(timeout=None)
    buttonCandidature = Button(label="Modifier la candidature",
                               style=discord.ButtonStyle.red, custom_id="candidate_edit", emoji="⚙️")

    async def button_callback(interaction: discord.Interaction):
        await interaction.response.send_modal(Candidature("test"))

    buttonCandidature.callback = button_callback
    view.add_item(item=buttonCandidature)
    await ctx.send(view=view) """


@bot.command()
async def votes(ctx):
    options = []

    await ctx.send(embed=discord.Embed(title="Jour des votes", description="Chers membres de la communauté, aujourd'hui est le grand jour des votes", color=0x007bff))

    participants = get_json_data("candidatures.json")

    for user_id, user_data in participants.items():
        participant = await bot.fetch_user(int(user_id))

        embed2 = discord.Embed(
            title=f"Participant {participant.global_name}",
            description=user_data[0],
            colour=0x007bff
        )

        embed2.add_field(name="Campagne", value=user_data[1], inline=False)
        embed2.add_field(name="Liens importants", value=user_data[2], inline=False)

        embed2.set_thumbnail(url=participant.avatar.url)

        options.append(discord.SelectOption(label=participant.global_name, value=participant.id))
        await ctx.send(embed=embed2)

    select = Select(placeholder="Votez ici", options=options)

    async def callbacks(interaction):
        selected_user_id = select.values[0]
        participant = await bot.fetch_user(selected_user_id)

        try:
            file_data = get_json_data("votes.json")
        except json.decoder.JSONDecodeError:
            file_data = {}

        if str(interaction.user.id) != str(selected_user_id):
            user_id = str(interaction.user.id)
            file_data[user_id] = selected_user_id

            save_json_data("votes.json", file_data)
            await interaction.response.send_message(f"Vous avez voté pour {participant.global_name}", ephemeral=True)
        else:
            await interaction.response.send_message("Vous ne pouvez pas voter pour vous-même !", ephemeral=True)

    select.callback = callbacks
    view = View(timeout=None)
    view.add_item(select)
    await ctx.send("Pour qui votez vous ?", view=view)


@bot.command()
async def winner(ctx):
    vote_counts = {}

    file_data = get_json_data("votes.json")

    for voted_for in file_data.values():
        if voted_for in vote_counts:
            vote_counts[voted_for] += 1
        else:
            vote_counts[voted_for] = 1

    max_count = max(vote_counts.values())
    winners = [user_votes for user_votes,
               count in vote_counts.items() if count == max_count]

    total_votes = sum(vote_counts.values())

    if len(winners) == 1:
        winner_user = await bot.fetch_user(winners[0])
        await ctx.send(f"Le gagnant est {winner_user.global_name} avec {max_count} votes!")
        for user_votes, count in vote_counts.items():
            percentage = (count / total_votes) * 100
            percentage_user = await bot.fetch_user(user_votes)
            await ctx.send(f"Le candidat {percentage_user.global_name} a été voté à {percentage:.2f}%")
    else:
        await ctx.send("Il y a une égalité entre plusieurs participants. Veuillez revoter pour départager!")
        candidates = get_json_data("candidatures.json")
        new_candidates = {str(candidate_id): candidates[str(
            candidate_id)] for candidate_id in winners}
        save_json_data("candidatures.json", new_candidates)
        save_json_data("votes.json", {})
        await ctx.invoke(ctx.bot.get_command('votes'))


@bot.command()
async def del_casier(ctx):
    messages = [message async for message in ctx.channel.history(limit=123, oldest_first=True)]

    if not messages:
        await ctx.send("Aucun message trouvé.")
        return

    posted_date = messages[0].created_at.date()
    today = datetime.now().date()

    days_difference = (today - posted_date).days

    if days_difference >= 15:
        await messages[0].delete()
        botMessage = await ctx.reply("Le dernier message a été supprimé", ephemeral=True)
        time.sleep(2)
        await botMessage.delete()
        await ctx.message.delete()
    else:
        botMessage = await ctx.reply("La suppression des messages est à jour", ephemeral=True)
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
