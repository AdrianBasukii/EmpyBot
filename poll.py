import nextcord

class PollBot():
    # Initializer function to define variables based on the parameters
    def __init__(self, question, options, thumbnail, pollCreator):
        self.question = question
        self.options = options
        self.thumbnail = thumbnail
        self.pollCreator = pollCreator
        self.embed = self.__createEmbed() # Creating a variable containing the embed
        
    # Function that returns an embed to show the poll question and options
    def __createEmbed(self):

        # Creating a new embed
        embed = nextcord.Embed(
        title=f"{self.question}",
        description="Select your options: ",
        color= nextcord.Colour.green(),
        )
        
        # Adding the properties of the poll
        embed.set_thumbnail(url=self.thumbnail)
        embed.set_footer(text=f"Poll created by {self.pollCreator}")

        # Creating a new field for every option
        for i, option in enumerate(self.options, start=1):
            embed.add_field(name=f"\u200b", value=f'{i}. {option}', inline=False)

        return embed

class PollBotResults():
    # Initializer function to define variables based on the parameters
    def __init__(self, pollMessage, question, options, thumbnail, pollCreator):
        self.pollMessage = pollMessage
        self.question = question
        self.options = options
        self.thumbnail = thumbnail
        self.pollCreator = pollCreator
        self.percentage = self.__percentageCalculator() # Creating a variable containing the percentage of votes for each option
        self.embed = self.__createEmbed() # Creating a variable containing the new embed

    # Function that returns a new embed to show the results of the poll
    def __createEmbed(self):

        # Embed creation
        embedAfter = nextcord.Embed(
        title="Poll has ended!",
        description=f"{self.question}",
        color= nextcord.Colour.green(),
        )

        # Adding properties 
        embedAfter.set_thumbnail(url=self.thumbnail)
        embedAfter.set_footer(text=f"Poll created by {self.pollCreator}")

        # Loops over the self.percentage list and adding a field for each member
        for optionPercentage in self.percentage:
            optionPercentage = optionPercentage.split(",") #Splitting each member of the list (string) into two parts: option and percentage for the option
            embedAfter.add_field(name=f"{optionPercentage[0]}", value=f'{optionPercentage[1]}', inline=False)

        return embedAfter

    # Function that calculates the percentage of votes for each option
    def __percentageCalculator(self):
        totalReactions = sum(reaction.count for reaction in self.pollMessage.reactions) - len(self.options) # Total number of reactions minus the bot's reactions

        # Checking if the total user reactions are 0 to prevent division by zero
        if totalReactions != 0:
            # Returning a list of results; each member of the list contains the option and a percentage bar along with the percentage
            return [f"{i}. {option}:, {'●'*round((100 * (reaction.count-1) / totalReactions)/10)}{'○'*(10-round((100 * (reaction.count-1) / totalReactions)/10))} | {100 * (reaction.count-1) / totalReactions:.2f}%" for i, option, reaction in zip(range(1, len(self.options) + 1), self.options, self.pollMessage.reactions)]
        else:
            # Returns same list of results as above, but the percentage bar only shows the unfilled circle
            return [f"{i}. {option}:, {'○'*10} | 0%" for i, option in zip(range(1, len(self.options) + 1), self.options, self.pollMessage.reactions)]