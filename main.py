import nextcord
from nextcord.ext import commands, tasks
import asyncio
import random
from typing import Optional # Used to make optional fields in slash commands
import aiohttp # Asynchronous HTTP Client/Server for Python and Asyncio

# Importing classes from other files
from weather import WeatherBot
from poll import PollBot, PollBotResults
from tictactoe import tttEmbed, tttMain

# Main Variables
TOKEN = '' # Discord Bot Token
API_KEY = '' # API KEY for Weather API 
bot = commands.Bot(command_prefix='-', intents = nextcord.Intents.all()) # Creating the bot with the prefix '-' and giving it access to information and events from nextcord API 

# Bot event that indicates the bot is online
@bot.event
async def on_ready():
    print("Empy Is Online!")
    reset_message_counts.start() # Starts the loop that resets the message count of each user every 3 seconds

bot.remove_command('help') # Removes the default help command from Nextcord

# Creating a new help command to show list of commands
@bot.slash_command(name="help", description="List of commands")
async def help(interaction: nextcord.Interaction):

    # Creating a new embed
    embed = nextcord.Embed(
        title="Welcome to EmpyBot!",
        description="EmpyBot is a multi purpose bot that is ready to be your versatile server companion. Keep it tidy, engage with polls, enjoy games, and stay informed about the weather effortlessly. \n \nHere are the **list of commands: **\n",
        color=nextcord.Colour.blue()
    )

    # Adding field for command categories
    embed.add_field(name=f"🛠️ Admin Commands", value="`/mute` - Mutes members \n  `/unmute` - Unmutes members \n `-clear` - Clears a specified number of messages", inline= False)
    embed.add_field(name=f"💬 User Commands", value="`/ttt` - Play tictactoe against your friends \n  `/tttsp` - Play tictactoe against the bot \n `/createpoll` - Create a poll \n `/weather` - Find weather information for a specified city", inline= False)
    embed.add_field(name=f"🎮 Tictactoe Commands", value="`-place` - Place a tile \n `-end` - End a game early", inline= False)

    # Sending the embed as a reply
    await interaction.response.send_message(embed=embed)

"""-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
---------------Server Moderation Features---------------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""

# PURGING MESSAGES
@bot.command()
@commands.has_permissions(administrator=True) # Makes sure that the user that wrote the message has administrator permissions
async def clear(ctx: commands.Context, *, number=0):
    
    # Prevents admins from deleting over 100 messages and making sure that the value they input is positive
    if number <= 100 and number>0:
        await ctx.channel.purge(limit=number+1)
    
    elif (number >= 100 or number<0): 
        await ctx.send("Please enter a value between `1` and `100`")

# Error handler for the clear command
@clear.error
async def clear_errorHandler(ctx: commands.Context, error):

    # Case where user does not have permissions to use it
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Only administrators are allowed to use this command!")

    # Case where the input is invalid
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid argument!")

    # Case where bot does not have permissions
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("Bot doesn't have permission to clear messages!")


# Muting Members
@bot.slash_command(name="mute", description="Mute members of your server!")
@commands.has_permissions(administrator=True) # Makes sure that the user that wrote the message has administrator permissions
async def mute(interaction: nextcord.Interaction, member: nextcord.Member, reason: str):
    
    guild = interaction.guild # Server where the interaction occured
    muteRole = nextcord.utils.get(guild.roles, name="Muted") # Getting the Muted role from the server

    # Case where the server (guild) does not have a "Muted" role
    if not muteRole:
        muteRole = await guild.create_role(name="Muted")

        # Iterating over every channel in the server
        for channel in guild.channels:
            await channel.set_permissions(muteRole, send_messages=False) # Removing permissions to send messages
     
    # Creating embed for the mute feature
    embed = nextcord.Embed(
        title=f"`{member.display_name}` has been muted!",
        description=f"Reason: `{reason}`",
        color = nextcord.Colour.dark_red(),
    )

    # Acquiring the member's avatar
    memberAvatar = member.avatar.url

    # Setting the avatar as thumbnail
    embed.set_thumbnail(url=memberAvatar)

    # Checking if the member is already muted
    if muteRole in member.roles:
        await interaction.response.send_message(f"`{member.display_name}` is already muted!")

    else: 
        # Adding the role and telling the user that they have been muted
        await member.add_roles(muteRole, reason=reason) # Adding role
        await interaction.response.send_message(embed=embed)
        await member.send(f"You have been muted in `{interaction.guild}` \n \n Reason: `{reason}`") # Sending a DM


# Unmuting Members
@bot.slash_command(name="unmute", description="Unmute members of your server!")
@commands.has_permissions(administrator=True) # Makes sure that the user that wrote the message has administrator permissions
async def unmute(interaction: nextcord.Interaction, member: nextcord.Member):
    
    guild = interaction.guild # Server where the interaction occured
    muteRole = nextcord.utils.get(guild.roles, name="Muted") # Getting the Muted role from the server
    
    # Checking if the server has the mute role
    if muteRole == None:
        await interaction.response.send_message("`'Muted'` role does not exist in this server!")

    # Checking if the member is currently muted
    elif muteRole not in member.roles:
        await interaction.response.send_message(f"`{member.display_name}` does not have `'Muted'` role!")
    else:
        await member.remove_roles(muteRole) # Removing role
        await interaction.response.send_message(f"`{member.display_name}` has been unmuted!")

# Error handler for the clear command
@mute.error
async def clear_errorHandler(ctx: commands.Context, error):

    # Case where user does not have permissions to use it
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Only administrators are allowed to use this command!")

    # Case where bot does not have permissions
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("Bot doesn't have permission!")

# Error handler for the clear command
@unmute.error
async def clear_errorHandler(ctx: commands.Context, error):

    # Case where user does not have permissions to use it
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Only administrators are allowed to use this command!")

    # Case where bot does not have permissions
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("Bot doesn't have permission to remove roles!")

# SPAM DETECTION

# Creating a dictionary to store message counts for different users
message_counts = {}

# Resetting the message counts every 3 seconds
@tasks.loop(seconds=3)
async def reset_message_counts():
    global message_counts
    message_counts = {}

# Bot event that constantly monitors the messages
@bot.event
async def on_message(message):

    # Update message count for the user
    user_id = message.author.id
    message_counts[user_id] = message_counts.get(user_id, 0) + 1

    # Check for spammy behavior 
    spamThresholdLevelOne = 3
    spamThresholdLevelTwo = 5

    # Giving a warning
    if message_counts[user_id] > spamThresholdLevelOne and message_counts[user_id] < spamThresholdLevelTwo:
        await message.channel.send(f"{message.author.mention}, please avoid spamming.")

    # Muting user for 5 minutes
    elif message_counts[user_id] > spamThresholdLevelTwo:
        guild = message.guild # Server where the message was sent
        muteRole = nextcord.utils.get(guild.roles, name="Muted") # Getting the Muted role from the server

        # Case where the server (guild) does not have a "Muted" role
        if not muteRole:
            muteRole = await guild.create_role(name="Muted")

            # Iterating over every channel in the server
            for channel in guild.channels:
                await channel.set_permissions(muteRole, send_messages=False) # Removing permissions to send messages
        
        # Sending messages and adding the "Muted" role
        await message.channel.send(f"{message.author.mention} You have been muted for **spamming**! Please wait `5 Minutes` before getting unmuted!")
        await message.author.add_roles(muteRole, reason="Spamming")

        await asyncio.sleep(300) # Pauses for 5 minutes asynchronously

        # Checking if muteRole is still in the user's roles list
        if muteRole not in message.author.roles:
            await message.channel.send(f"{message.author.mention} You have been unmuted! Please avoid spamming next time!")
            await message.author.remove_roles(muteRole)

    await bot.process_commands(message) # Triggers the function when messages are received

# POLLS
@bot.slash_command(name="createpoll", description="Create a poll")
async def create_poll(
    interaction: nextcord.Interaction,
    channel: nextcord.TextChannel,
    pollminutes: int,
    question: str, 
    option1: str, 
    option2: str, 
    option3: Optional[str],
    option4: Optional[str],
    option5: Optional[str],
    thumbnail: Optional[str],
    ):

    # Defining the creator of the poll
    pollCreator = interaction.user

    # Sets the value of thumbnail to the default thumbnail if user did not put a custom thumbnail
    if thumbnail == None:
        thumbnail = '' 

    # Creating the list of options based on the input
    optionsList = [option1, option2, option3, option4, option5]
    
    # Removes None type members in options list (if any)
    while(None in optionsList):
        optionsList.remove(None)

    embed = PollBot(question,optionsList, thumbnail, pollCreator).embed # Create a new embed from the class PollBot

    if pollminutes > 0: 
        await interaction.response.send_message(f"Poll has been created successfully in `{channel}`!") # Replying to user with a message
        pollMessage = await channel.send(embed=embed) # Sending embed in the channel

        # Adding number emoji reactions according to the number of options that the user inputted 
        for i in range(1, len(optionsList) + 1):
            await pollMessage.add_reaction(f"{i}\u20e3")

        await asyncio.sleep(pollminutes*60) # Waits for the specified amount of time before doing the next actions
            
        pollMessage = await channel.fetch_message(pollMessage.id) # Fetches the id of the previously sent message

        botReactions = [] # A list of reactions where the bot is the author

        # Iteration over reactions in pollMessage
        for reaction in pollMessage.reactions:

            # Asynchronous iteration over the users who added reactions
            async for user in reaction.users():
                if user.bot:
                    botReactions.append(reaction) # Appends to botReactions list if it is the case where the author is the bot

        # Another iteration over reactions in pollMessage
        for reaction in pollMessage.reactions:
            # Checks if any reactions are not the same as the ones that the bot provided
            if reaction not in botReactions:
                await pollMessage.clear_reaction(reaction) # Removes the extra reactions added by users

        pollMessage = await channel.fetch_message(pollMessage.id) # Fetches the id of the previously sent message

        embedAfter = PollBotResults(pollMessage, question,optionsList, thumbnail, pollCreator).embed # Creating a new embed with the results

        await pollMessage.clear_reactions() # Clears all reactions on the poll
        await pollMessage.edit(embed=embedAfter) # Edits the previous message by replacing the embed with the results embed
    
    else:
        await interaction.response.send_message("Please input a **positive integer!**")

@create_poll.error
async def create_poll_errorHandler(ctx: commands.Context, error):
    await ctx.send("Poll could not be created due to invalid URL!")

"""-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
---------------Games--------------------------------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""

#--TIC TAC TOE-------------------------------------------------------------------------------------------------------------------------------------------------------------

# Setting default values for the global variables
player1 = ""
player2 = ""
turn = ""
gameOver = True
board = []
blunderProbability = 0

# Winning conditions for the game
winningConditions = [
    [0, 1, 2],  # Top row
    [3, 4, 5],  # Middle row
    [6, 7, 8],  # Bottom row
    [0, 3, 6],  # Left column
    [1, 4, 7],  # Middle column
    [2, 5, 8],  # Right column
    [0, 4, 8],  # Diagonal from top-left to bottom-right
    [2, 4, 6],  # Diagonal from top-right to bottom-left
]

# Main slash command that starts the game
@bot.slash_command(name="ttt", description="Play Tic Tac Toe with your friends!")
async def ttt(interaction: nextcord.Interaction, p1: nextcord.Member, p2: nextcord.Member):

    # Accessing global variables
    global player1
    global player2
    global turn
    global gameOver
    global board
    global count

    # Checking if player 1 is the same as player 2
    if p1 != p2:

        # Checking if any game is started
        if gameOver:

            # Changing the board into 9 square tiles
            board = [":white_large_square:",":white_large_square:",":white_large_square:",
                    ":white_large_square:",":white_large_square:",":white_large_square:",
                    ":white_large_square:",":white_large_square:",":white_large_square:",]
        
            turn = "" 
            gameOver = False # Game has been started
            count = 0 # Number of turns that have been taken


            # Players
            player1 = p1
            player2 = p2

            # Determining who takes the first turn
            turnNum = random.randint(1,2)
            if turnNum == 1:
                turn = player1
            elif turnNum == 2:
                turn = player2

            # Creating embed using a function from the tttEmbed class
            embed = tttEmbed(board, player1, player2, turn, count).embed

            # Bot replies to the user with the created embed
            await interaction.response.send_message(embed=embed, content=f"A TicTacToe match of {player1.mention} against {player2.mention} has begun!")

        else:
            await interaction.response.send_message("A game is currently in progress!")
    else:
        await interaction.response.send_message("Players must be different for the game to start!")

# Command to place the tiles/marks
@bot.command()
async def place(ctx: commands.Context, pos: int):

    # Accessing global variables
    global player1
    global player2
    global turn
    global count
    global board
    global gameOver

    # Conditions that check if the game is over and checks if the one who wrote the -end command are any of the players
    if not gameOver and (ctx.author.id == player1.id or ctx.author.id == player2.id):

        #Creating new variables
        mark = "" # Variable to change the white tiles into marks (Either O or X)
        tttMainFunctions = tttMain(player1, player2, mark, turn) # Creating new object for several functions

        # Checks if the author of the message is the player who is the turn
        if turn == ctx.author:
            mark = tttMainFunctions.newMark

            # Checks if position value is valid (integer between 1-9) and check if the tile is unmarked
            if 0 < pos < 10 and board[pos-1] == ":white_large_square:":
                board[pos-1] = mark # Changing the emoji on the board to a mark
                count += 1 # Adds the number of turns by 1

                # Creating a new, updated embed with the mark
                embed = tttEmbed(board, player1, player2, turn, count).embed

                # Bot sends the embed
                await ctx.send(embed=embed)

                # Checking if there is a winner
                checkWinner(winningConditions, mark)

                # Checks the status of gameOver (T/F) after running the checkWinner function
                if gameOver:
                    # find the winner based on what the value of the mark
                    if mark == ":regional_indicator_x:":
                        await ctx.send(f"{player1.mention} Wins!") 
                    elif mark == ":o2:":
                        await ctx.send(f"{player2.mention} Wins!") 

                # Check if it reached total amount of turns it is possible to take
                elif count >= 9: 
                    await ctx.send(f"It's a tie!")
                    gameOver = True
                    

                # Switching turns
                turn = tttMainFunctions.switchTurns

                if turn == "Bot":
                    await makeBotMove(ctx)

            # Case where tile is marked
            elif 0 < pos < 10 and board[pos-1] != ":white_large_square:":
                await ctx.send("Please select an **unmarked tile!**")
            
            # Other cases where pos may be greater than 9
            else:
                await ctx.send("Please choose an integer between **1 and 9**")

        else:
            await ctx.send("Please wait for your turn!")

    elif gameOver:
        await ctx.send("Please start a new game using `/ttt`")

# Command to end the game before it finishes
@bot.command()
async def end(ctx: commands.Context):
    # Accessing global variables
    global gameOver
    global player1
    global player2

    # Conditions that check if the game is over and checks if the one who wrote the -end command are any of the players
    if not gameOver and (ctx.author == player1 or ctx.author == player2):
        gameOver = True
        await ctx.send("Current game has been ended!")
    
    elif (player1 != "" and player2 != "") and (ctx.author != player1 or ctx.author != player2):
        await ctx.send("Only players can use this command!")

    elif gameOver:
        await ctx.send("A game has not been started!")


# Function to check if a winning condition is reached
def checkWinner(winningConditions, mark):
    global gameOver

    # Iterates over the list of winning conditions
    for condition in winningConditions:
        # Checking if the marks are in the position that gives the winning condition, then ending the game once the condition is fulfilled
        if board[condition[0]] == mark and board[condition[1]] == mark and board[condition[2]] == mark:
            gameOver = True


# Error handlers for the -place command
@place.error
async def place_errorHandler(ctx: commands.Context, error):
    #Check if the error is a certain type
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please enter a position you would like to mark!") 
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to enter an integer!")


# TICTACTOE Against Bot
@bot.slash_command(name="tttsp", description="Play Tic Tac Toe against the bot!")
async def tttsingleplayer(
    interaction: nextcord.Interaction, 
    difficulty: str = nextcord.SlashOption(
        name="difficulties",
        choices=["Easy", "Medium", "Hard"],
        required=True,
    )):
    # Accessing global variables
    global player1
    global player2
    global gameOver
    global blunderProbability
    global turn
    global count
    global board

    # Checking if any game is started
    if gameOver:
        
        # Adjusting the difficulty by changing the probability of blundering
        if difficulty == "Easy":
            blunderProbability = 0.6
        elif difficulty == "Medium:":
            blunderProbability = 0.4
        elif difficulty == "Hard":
            blunderProbability = 0.1


        # Changing the board into 9 square tiles
        board = [":white_large_square:",":white_large_square:",":white_large_square:",
                    ":white_large_square:",":white_large_square:",":white_large_square:",
                    ":white_large_square:",":white_large_square:",":white_large_square:",]

        turn = "" 
        gameOver = False  # Game has been started
        count = 0  # Number of turns that have been taken

        # Players
        player1 = interaction.user
        player2 = "Bot"

        # Determining who takes the first turn
        turnNum = random.randint(1, 2)
        if turnNum == 1:
            turn = player1
        elif turnNum == 2:
            turn = player2

        # Creating embed using tttEmbed class
        embed = tttEmbed(board, player1, player2, turn, count).embed

        # Bot replies to the user with the created embed
        await interaction.response.send_message(embed=embed, content=f"A single-player Tic Tac Toe match against the AI has begun!")

        # Determining what asynchronous functions should be run based on the turn
        if turn == "Bot":
            await makeBotMove(interaction) # Runs the bot move function

        else:
            await place(interaction) # Runs the place tile function

    else:
        await interaction.response.send_message("A game is currently in progress!")

# Function to make a move for the Bot
async def makeBotMove(ctx: commands.Context):
    # Accessing global variables
    global turn
    global count
    global board
    global gameOver
    global blunderProbability

    mark = ":o2:"  # Bot's mark
    tttMainFunctions = tttMain(player1, player2, mark, turn)  # Creating new object for several functions

    # Check for a winning move
    
    if not gameOver:

        # Introduce occasional blunders according to the probability that was defined based on the difficulty chosen
        if random.random() < blunderProbability:
            print("blunder!")
            pos = random.randint(1, 9)
            while board[pos - 1] != ":white_large_square:":
                pos = random.randint(1, 9)
            board[pos - 1] = mark  
            count += 1

        # Uses the MINIMAX algorithm when not blundering
        else:
            best_move = getBestMove(board) # Getting the best move through the minimax algorithm functions
            board[best_move] = mark  # Replacing the position with a mark
            count += 1  # Adds the number of turns by 1

        # Creating a new, updated embed with the mark
        embed = tttEmbed(board, player1, player2, turn, count).embed

        # Bot sends the embed
        await ctx.send(embed=embed)

        # Checking if there is a winner
        checkWinner(winningConditions, mark)

        # Checks the status of gameOver (T/F) after running the checkWinner function
        if gameOver:
            # find the winner based on what the value of the mark
            if mark == ":regional_indicator_x:":
                await ctx.send(f"{player1.mention} Wins!")
            elif mark == ":o2:":
                await ctx.send("`Bot` Wins!")

        # Check if it reached the total number of turns it is possible to take
        elif isBoardFull(board):
            await ctx.send("It's a tie!")
            gameOver = True

        # Switching turns
        turn = tttMainFunctions.switchTurns

# Function that returns a list of unmarked positions in the board (white large squares)
def getAvailableMoves(board):
    return [index for index, value in enumerate(board) if value == ":white_large_square:"]

# Function that returns values based on the status of the game
def evaluate(board):
    # Check for a win, lose, or draw
    winner = checkWinnerSP(board)
    if winner == ":o2:":
        return 1  # Bot wins
    elif winner == ":regional_indicator_x:":
        return -1  # Opponent wins
    elif isBoardFull(board):
        return 0  # It's a draw
    else:
        return None  # Game is not over yet

# Function that checks for winners
def checkWinnerSP(board):
    # Check for each condition from the winningConditions list
    for condition in winningConditions:
        # Checking if there is a diagonal, vertical, or horizontal row of the same marks (not white tiles)
        if board[condition[0]] == board[condition[1]] == board[condition[2]] and board[condition[0]] != ":white_large_square:":
            return board[condition[0]]  # Return the winning player's mark
    return None  # No winner

# Function that checks if the board is full (no more white tiles on the board)
def isBoardFull(board):
    return ":white_large_square:" not in board

# Function to apply the minimax algorithm, where:
# BOARD --> Current state of the board
# DEPTH --> Current depth in the game tree which represents how many moves ahead the algorithm should explore.
# MAXIMIZING PLAYER --> Boolean indicating whether current player is the maximizing player (bot) or not
def minimax(board, depth, maximizing_player):
    # Check if the game has ended or if the depth limit is reached
    score = evaluate(board)
    if score is not None or depth == 0:
        return score

    # Checking the boolean value 
    if maximizing_player:
        max_eval = float('-inf') # Setting initial value to maximum evaluation score to negative infinity

        # Assume bot's move and recursively call minimax for the opponent's move
        for move in getAvailableMoves(board):
            board[move] = ":o2:"  # Bot's mark
            eval_score = minimax(board, depth - 1, False)
            board[move] = ":white_large_square:"  # Undo the move

            # Update the maximum evaluation score
            max_eval = max(max_eval, eval_score)

        return max_eval
    
    else:
        # If the current player is the opponent (minimizing player)
        min_eval = float('inf') # Setting initial value to minimum evaluation score to infinity

        # Assume opponent's move and recursively call minimax for the bot's move
        for move in getAvailableMoves(board):
            board[move] = ":regional_indicator_x:"  # Opponent's mark
            eval_score = minimax(board, depth - 1, True)
            board[move] = ":white_large_square:"  # Undo the move

            # Update the minimum evaluation score
            min_eval = min(min_eval, eval_score)

        return min_eval

# Function to get the best move
def getBestMove(board):
    # Initialize variables to track the best move and its score
    best_score = float('-inf')
    best_move = None

     # Iterate through available moves
    for move in getAvailableMoves(board):
        board[move] = ":o2:"  # Bot's mark
        move_score = minimax(board, 9, False)  # 9 is the maximum depth in Tic Tac Toe
        board[move] = ":white_large_square:"  # Undo the move

        # Compare move's score with the current best score
        if move_score > best_score:

            # Update the best move and its score
            best_score = move_score
            best_move = move

    # Return the best move found after exploring all available moves
    return best_move

"""-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
---------------Miscellaneous Features---------------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""

# WEATHER BOT
@bot.slash_command(name="weather", description="Get current weather for a city")
async def weather(interaction: nextcord.Interaction, city: str):
    url = "https://api.weatherapi.com/v1/current.json" # Retrieves the current weather in JSON format
    params = {
        "key": API_KEY, # API key used to authenticate the request
        "q": city # Query parameter for the city you want to get the weather information for
    }
    
    # Creating an asynchronous context
    async with aiohttp.ClientSession() as session:

        # Perform an asynchronous HTTP GET request to the specified url with the specified parameters
        async with session.get(url, params=params) as res:

            # Reading the response body (res) and parses it as JSON
            data = await res.json()

            # Creating embed using the weatherbot class from weather.py file
            weatherBot = WeatherBot(data) 
            embed = weatherBot.embed
            
            # Sending the embed as message
            await interaction.response.send_message(embed=embed)

"""-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
---------------Activating the bot-------------------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""

bot.run(TOKEN)
