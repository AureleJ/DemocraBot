import discord
import settings
from discord.ext import commands
from discord import app_commands
from datetime import date
import time

class MyBot(commands.Bot):
    def __init__(self, command_prefix='!', intents=None):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.vote_counts = {}
        self.member_votes = {}

        intents = discord.Intents.default()
        client = discord.Client(intents=intents)
        tree = app_commands.CommandTree(client)
        intents.message_content = True
        intents.guilds = True
        intents.members = True

        self.add_command(self.voltaire)
        self.add_command(self.maxence)
        self.add_command(self.aurele)
        self.add_command(self.ping)
        self.add_command(self.lois)
        self.add_command(self.votes)
        self.add_command(self.result)
        self.add_command(self.avatar)
        self.add_command(self.dele)

        self.add_listener(self.on_ready_event)
        self.add_listener(self.on_command_error_event)

    async def on_ready_event(self):
        print(f'Logged on as {self.user}!')
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} commands")
        except Exception as e:
            print(e)

    async def on_command_error_event(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Command not found.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing required argument.")

    @commands.hybrid_command()
    async def voltaire(self, ctx, *, message):
        await ctx.send(f"{message} : https://www.projet-voltaire.fr/")

    @commands.hybrid_command()
    async def maxence(self, ctx):
        await ctx.send('Il a un petit train <:MAXENCE:1174633349994791042>')

    @commands.hybrid_command()
    async def aurele(self, ctx):
        await ctx.send("c'est le plus bo")

    @commands.hybrid_command(name="ping", description="Make ping test")
    async def ping(self, ctx, message=None):
        if message is None:
            await ctx.send("Il manque un argument")
        else:
            await ctx.send('pong')

    @commands.command()
    async def lois(self, ctx):
        with open('lois.txt', 'r') as file:
            content = file.read()
        await ctx.send(content)

    @commands.command()
    async def votes(self, ctx):
        embed = discord.Embed(title="Jour des votes", description="Chers membres de la communauté, aujourd'hui est le grand jour des votes", color=0x007bff)

        participants = {
            410111790970568705: ["Campagne", "Liens"],
            328542368037076992: ["Campagne", "Liens"],
            455059373941587988: ["Campagne", "Liens"],
            712954659773480963: ["Campagne", "Liens"]
        }

        for participant_id, data in participants.items():
            user = await self.fetch_user(participant_id)

            embed2 = discord.Embed(
                title=f"Participant {user.name}",
                description="Description personnelle",
                colour=0x007bff
            )

            embed2.add_field(name="Campagne", value=data[0], inline=True)
            embed2.add_field(name="Liens importants", value=data[1], inline=True)

            embed2.set_thumbnail(url=user.avatar.url)

            await ctx.send(embed=[embed, embed2])
            await ctx.send(view=MyView(user.name, self))

    @commands.command()
    async def result(self, ctx):
        if self.member_votes:
            winner = max(self.vote_counts, key=self.vote_counts.get, default="Le vote n'est pas encore terminé")
            await ctx.send(f"Le vainqueur est : {winner}")

    @commands.hybrid_command()
    async def avatar(self, ctx, *, member: discord.Member = None):
        user_avatar_url = member.avatar.url if member else ctx.author.avatar.url
        await ctx.send(user_avatar_url)

    @commands.command()
    async def dele(self, ctx):
        messages = [message async for message in ctx.channel.history(limit=123, oldest_first=True)]
        posted = messages[0].created_at.date().strftime('%d')
        today = date.today().strftime('%d')
        if int(today) - int(posted) >= 15:
            await messages[0].delete()
            bot_message = await ctx.reply("Le dernier message a été supprimé", ephemeral=True)
            time.sleep(2)
            await bot_message.delete()
            await ctx.message.delete()
        else:
            bot_message = await ctx.reply("La suppression des messages est à jour", ephemeral=True)
            time.sleep(2)
            await bot_message.delete()
            await ctx.message.delete()

class MyView(discord.ui.View):
    def __init__(self, participant_name: str, bot_instance: MyBot):
        super().__init__()
        self.participant_name = participant_name
        self.bot_instance = bot_instance

    @discord.ui.button(label="Vote", style=discord.ButtonStyle.green)
    async def button_callback(self, interaction: discord.Integration, button: discord.ui.Button):
        self.bot_instance.vote_counts[self.participant_name] = self.bot_instance.vote_counts.get(self.participant_name, 0) + 1
        self.bot_instance.member_votes[interaction.user.name] = self.participant_name
        print(f"Vote pour {self.participant_name}. Nombre total de votes : {self.bot_instance.vote_counts}")
        print(self.bot_instance.member_votes)
        await interaction.response.send_message(f"Vous avez voté pour {self.participant_name}", ephemeral=True)

# Use the MyBot class directly
bot = MyBot(command_prefix='!', intents=intents)
bot.run(settings.api_key)
