import discord
import settings
from discord.ext import commands
from discord import app_commands
from datetime import date
import time

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
async def maxence(ctx):
    await ctx.send('Il a un petit train <:MAXENCE:1174633349994791042>')


@bot.hybrid_command()
async def aurele(ctx):
    await ctx.send("c'est le plus bo")


@bot.hybrid_command(name="ping", description="Make ping test")
async def ping(ctx, message):
    if message == None:
        await ctx.send("Il manque un argument")
    await ctx.send('pong')

""" @bot.event
async def on_message(message):
    print(f'Message from {message.author}: {message.content}')
    await bot.process_commands(message) """


@bot.command()
async def lois(ctx):
    await ctx.send(lois.txt)


@bot.command()
async def votes(ctx):
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
member_votes={}

class MyView(discord.ui.View):
    def __init__(self, participant_name: str):
        super().__init__()
        self.participant_name = participant_name

    @discord.ui.button(label="Vote", style=discord.ButtonStyle.green)
    async def button_callback(self, interaction: discord.Integration, button: discord.ui.Button):
        vote_counts[self.participant_name] = vote_counts.get(self.participant_name, 0) + 1
        member_votes[interaction.user.name] = self.participant_name
        print(f"Vote pour {self.participant_name}. Nombre total de votes : {vote_counts}")
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
