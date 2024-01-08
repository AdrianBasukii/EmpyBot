import nextcord

class WeatherBot():
    # Initializer function to define variables based on the JSON data
    def __init__(self, data):
        self.location = data["location"]["name"]
        self.localTime = data["location"]["localtime"].split()
        self.temp_c = data["current"]["temp_c"]
        self.temp_f = data["current"]["temp_f"]
        self.humidity = data["current"]["humidity"]
        self.wind_kph = data["current"]["wind_kph"]
        self.wind_mph = data["current"]["wind_mph"]
        self.last_updated = data["current"]["last_updated"]
        self.condition = data["current"]["condition"]["text"]
        self.image_url = "http:" + data["current"]["condition"]["icon"]
        self.__embedColor = nextcord.Colour.orange() # Default value for embed's color
        self.__tempChecker() # Changing the embed color value based on the temperature (in degrees celcius)
        self.embed = self.__createEmbed() # Creating a variable containing the embed

    # Function to check the temperature of the region (in degrees celcius) to decide the color of the embed
    def __tempChecker(self):
        if int(self.temp_c) >= 35:
            self.__embedColor = nextcord.Colour.orange()
        elif int(self.temp_c) < 35 and int(self.temp_c) >= 25:
            self.__embedColor = nextcord.Colour.yellow()
        elif int(self.temp_c) < 25 and int(self.temp_c) >= 10:
            self.__embedColor = nextcord.Colour.blue()
        elif int(self.temp_c) < 10:
            self.__embedColor = nextcord.Colour.dark_blue()
    
    # Function that returns an embed
    def __createEmbed(self):

        # Creating a new embed
        embed = nextcord.Embed(
                title=f"Showing Weather for {self.location}", 
                description=f"The conditions for `{self.location}` is `{self.condition}` ",
                color = self.__embedColor,
            )
        
        # Adding new properties to embed based on the provided information
        embed.add_field(name="Local Time", value=f"Date: {self.localTime[0]} \n Time: {self.localTime[1]}", inline= False)
        embed.add_field(name="", value=f"", inline= False)
        embed.add_field(name="Temperature", value=f"{self.temp_c} °C / {self.temp_f} °F", inline= False)
        embed.add_field(name="", value=f"", inline= False)
        embed.add_field(name="Humidity", value=f"{self.humidity}%", inline= False)
        embed.add_field(name="", value=f"", inline= False)
        embed.add_field(name="Wind Speed", value=f"{self.wind_kph} KPH / {self.wind_mph} MPH", inline= False)
        embed.add_field(name="", value=f"", inline= False)
        embed.set_thumbnail(url=self.image_url)
        embed.set_footer(text=f"Last Updated: {self.last_updated}")

        return embed