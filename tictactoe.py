import nextcord

# A class to create embeds for the tic tac toe game
class tttEmbed():
    def __init__(self, board, p1, p2, turn, count):
        self.p1 = p1
        self.p2 = p2
        self.board = board
        self.turn = turn
        self.count = count
        self.embed = self.__createEmbed()

    def __createEmbed(self):
        embed = nextcord.Embed(
                    title=f"Tic Tac Toe", 
                    description=f"`{self.p1}` **Vs.** `{self.p2}`\n ",
                )

        for x in range(0, len(self.board)-1, 3):
            embed.add_field(name="", value=f"{self.board[x]}   {self.board[x+1]}   {self.board[x+2]}", inline=False)
        
        if self.count > 0 and self.turn == self.p1:
            embed.set_footer(text=f"It's {self.p2}'s turn")
        elif self.count > 0 and self.turn == self.p2:
            embed.set_footer(text=f"It's {self.p1}'s turn")
        elif self.count == 0:
            embed.set_footer(text=f"It's {self.turn}'s turn")

        return embed
    
# A class that contains a few functions for the tic tac toe game
class tttMain():
    def __init__(self, p1, p2, mark, turn):
        self.p1 = p1
        self.p2 = p2
        self.mark = mark
        self.turn = turn
        self.newMark = self.__defineMark()
        self.switchTurns = self.__switchingTurns()

    # A function to define/switch the mark based which player's turn it is
    def __defineMark(self):
        if self.turn == self.p1:
            return ":regional_indicator_x:"
        elif self.turn == self.p2:
            return ":o2:"
    # A function that switches the turns
    def __switchingTurns(self):

        # Checking which player's turn it is, then returning the value of the other player
        if self.turn == self.p1:
            return self.p2
        elif self.turn == self.p2:
            return self.p1
    