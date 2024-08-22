from typing import Final
import os
from dotenv import load_dotenv
import datetime
import discord
import sqlite3
from responses import get_response

# STEP 0: LOAD OUR TOKEN FORM SOMEWHERE SAFE
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# STEP 1: BOT SETUP
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guild_messages = True
intents.reactions = True
intents.messages = True
intents.guilds = True
client = discord.Client(intents=intents)

# Testing
'''
send_signup_message = False
GUILD_ID = '1257380294613532794'
CHANNEL_ID = '1257380294613532798'
SIGNUP_ID = '1265783618232389693'
UPDATES_ID = '1265783648854999175'
ELO_ID = '1265783671189798985'
WR_ID = '1265783682069692529'
PEAK_ID = '1265783692312187005'
'''
# TOS 

GUILD_ID = '1243949692602286260'
CHANNEL_ID = '1258670047635705927'

send_signup_message = False
SIGNUP_ID = '1260747961751572571'
UPDATES_ID = '1260746530407710900'
ELO_ID = '1260748051010555974'
WR_ID = '1260748090076299307'
PEAK_ID = '1260748111060668426'


FORM_URL = 'https://form.jotform.com/241896070237056'

# STEP 2: MESSAGE FUNCTIONALITY
async def send_message(message, user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled, probably)')
        return
    try:
        if user_message[:2] == 't?':
            user_message = user_message[2:]
            response: str = get_response(user_message)
            await message.author.send(response) 
        elif user_message[:2] == 't!':    
            user_message = user_message[2:]
            response: str = get_response(user_message)
            message.channel.send(response)
    except Exception as e:
        print(e)

# STEP 3: HANDLING THE STARTUP FOR OUR BOT
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')
    guild = discord.utils.get(client.guilds, id=int(GUILD_ID))
    channel = discord.utils.get(guild.channels, id=int(CHANNEL_ID))
    # Get the day of the week as an integer (Monday=0, Sunday=6)
    today = datetime.datetime.today()
    day_of_week = today.weekday()
    ranked_role = discord.utils.get(guild.roles, name = "❰ RANKED ❱")
    # On Friday, open leaderboard submissions
    if send_signup_message: 
        # Create an embed with the Google Forms link
        channel = discord.utils.get(guild.channels, id=int(SIGNUP_ID))
        embed = discord.Embed(title="🏡 ToS2 Weekly Leaderboard Survey", 
                            description=f"Hello Ranked players! Please fill out this week's survey so we can update the leaderboard.",
                            color=0x00ff00)
        embed.add_field(name="JotForm", value=f"[ToS2 Leaderboard Update Form]({FORM_URL})", inline=False)
        embed.set_footer(text="Thank you for your participation! Submissions close on Monday 12AM PST.")
        embed.set_image(url="https://i.imgur.com/4zjbDCw.gif")

        # Send the embed message to the channel
        await channel.send(ranked_role.mention)
        await channel.send(embed=embed)

    # On Monday, post the weekly leaderboard
    
    if day_of_week == 2:
        channel = discord.utils.get(guild.channels, id=int(UPDATES_ID))
        await channel.send(f"🏡 **WEEKLY LEADERBOARD UPDATE**")
        db_file = 'leaderboard.db'
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        embeds = []
        weekly_winners = []
        weekly_names = []
        statement = '''SELECT *
                        FROM leaderboard
                        WHERE date BETWEEN DATE('now', '-7 days') AND DATE('now')
                        ORDER BY elo DESC
                        LIMIT 15;'''
        players_by_elo = cursor.execute(statement)
        ldb = ''
        for index, player in enumerate(players_by_elo, start=1):
            user = discord.utils.get(guild.members, name = player[0])
            mention = user.mention if user else player[0]
            if index < 4:
                weekly_names.append(mention)
                if user:
                    weekly_winners.append(user)
            ldb += get_leaderboard_entry(index, mention, player[1], f"[{player[2]}]")
        elo_page = discord.Embed(title="Weekly Elo Leaderboard 🟢",
                               description=ldb,
                               color=0x00ff00)
        embeds.append(elo_page)
        channel = discord.utils.get(guild.channels, id=int(ELO_ID))
        await channel.send(embed=elo_page)

        

        statement = '''SELECT *
                        FROM leaderboard
                        WHERE date BETWEEN DATE('now', '-7 days') AND DATE('now')
                        ORDER BY (CAST(wins AS FLOAT)/(wins + losses + draws)) DESC
                        LIMIT 15;'''
        players_by_wr = cursor.execute(statement)
        ldb = ''
        for index, player in enumerate(players_by_wr, start=1):
            user = discord.utils.get(guild.members, name = player[0])
            mention = user.mention if user else player[0]
            ldb += get_leaderboard_entry(index, mention, player[1], f"[{str(round(player[4]/sum(player[4:7])*100, 1))}%]")
        wr_page = discord.Embed(title="Weekly Win Rate Leaderboard 🟣",
                               description=ldb,
                               color=0xffc0cb)
        embeds.append(wr_page)
        channel = discord.utils.get(guild.channels, id=int(WR_ID))
        await channel.send(embed=wr_page)



        statement = '''SELECT *
                        FROM leaderboard
                        ORDER BY peak DESC
                        LIMIT 15;'''
        players_by_peak = cursor.execute(statement)
        ldb = ''
        for index, player in enumerate(players_by_peak, start=1):
            user = discord.utils.get(guild.members, name = player[0])
            mention = user.mention if user else player[0]
            ldb += get_leaderboard_entry(index, mention, player[1], f"[Peak: {player[3]}] - [Elo: {player[2]}] - [WR: {str(round(player[4]/sum(player[4:7])*100, 1))}%]")
        peak_page = discord.Embed(title="All Time Leaderboard 🟠",
                               description=ldb,
                               color=0xffa500)
        embeds.append(peak_page)
        channel = discord.utils.get(guild.channels, id=int(PEAK_ID))
        await channel.send(embed=peak_page)

        view = PaginatorView(embeds)
        channel = discord.utils.get(guild.channels, id=int(UPDATES_ID))
        await channel.send(embed=embeds[0], view=view)

        if len(weekly_names) < 3:
            await channel.send("Not enough players registered this week 😔")
        else:
            winner_role = discord.utils.get(guild.roles, name = "【 WEEKLY CHAMPION 】")
            winners_message = f'''🎉 **Congratulations** to our top performers in this week's Salem Showdown! 🏆\n
    🥇 First Place: {weekly_names[0]}\n
    🥈 Second Place: {weekly_names[1]}\n
    🥉 Third Place: {weekly_names[2]}\n
**Winners are given the honorary {winner_role.mention} role for their efforts**. Thank you to all participants and don't worry if you didn't win this time - *we still have more trials remaining!* 🧙‍♂️ 👏'''
            



            # Remove and add roles to old and new winners
            await channel.send(winners_message)
            past_winners = [member for member in guild.members if winner_role in member.roles]
            for winner in past_winners:
                await winner.remove_roles(winner_role)
            for winner in weekly_winners:
                await winner.add_roles(winner_role)
   



# STEP 4: HANDLING INCOMING MESSAGES
@client.event
async def on_message(message) -> None:
    if message.author == client.user:
        return
    
    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')
    await send_message(message, user_message)

# HELPER FUNCTION
def get_leaderboard_entry(index, name, ingame, value):
    res = ""
    prizes = {1: '🥇', 2: '🥈', 3: '🥉'}
    res += f'**{prizes[index]}. ' if index in prizes else f'{index}. '
    res += f'{name}\t'
    if ingame != "":
        res += f'({ingame})\t'
    res += f" - {value}"
    if index in prizes: 
        res += '**'
    return res + '\n'    

class PaginatorView(discord.ui.View):
    def __init__(self, embeds):
        super().__init__()
        self.embeds = embeds
        self.show_elo.disabled = True

    def update_buttons(self, index):
        for i in range(3):
            self.children[i].disabled = True if i == index else False

    @discord.ui.button(label="Weekly Elo", style=discord.ButtonStyle.primary)
    async def show_elo(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.update_buttons(0)
        await interaction.response.edit_message(embed=self.embeds[0], view=self)

    @discord.ui.button(label="Weekly WR", style=discord.ButtonStyle.primary)
    async def show_wr(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.update_buttons(1)
        await interaction.response.edit_message(embed=self.embeds[1], view=self)

    @discord.ui.button(label="Overall", style=discord.ButtonStyle.primary)
    async def show_peak(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.update_buttons(2)      
        await interaction.response.edit_message(embed=self.embeds[2], view=self)



# STEP 6: MAIN ENTRY POINT
def main() -> None:
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()


    


