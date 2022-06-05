
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv

import time
import discord
from discord.ext import commands

import os

#Web scrapping

URL_TTC = "https://www.ttc.ca/service-alerts"

station_xpath = "//*[@id='station-updates']/div/ul"
bus_xpath="//*[@id='bus-updates']"
train_xpath="//*[@id='train-updates']/div/ul"

#TTC EMBEDS HELPERS --------------------------------------------------------

def ttcEmbed_reg(data,pic,lastUpdated): # Create embed for alerts with bus/train number 
    embed=discord.Embed(title=data[0],  description=" ".join(data[1:]), url="https://www.ttc.ca/service-alerts", color=0xff0000)
    embed.set_thumbnail(url=pic)
    embed.add_field(name="Last updated", value=lastUpdated, inline=False)
    embed.set_footer(text="https://www.ttc.ca/service-alerts")
    return embed

def ttcEmbed_odd(data,pic,lastUpdated): # Create embed for other alerts
    embed=discord.Embed(title="Other Updates", url="https://www.ttc.ca/service-alerts", description=data[0], color=0xff0000)
    embed.set_thumbnail(url=pic)
    embed.add_field(name="Last updated", value=lastUpdated, inline=False)
    embed.set_footer(text="https://www.ttc.ca/service-alerts")
    return embed


#TTC SERVICE ALERTS --------------------------------------------------------
def get_TTCStatus(URL,option,number):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(URL)

    # Select all alerts
    items = driver.find_elements(by=By.CLASS_NAME,value ="AlertInformation_wrapperAlertItem__WCG7d")
   
    ttc_alerts=[]
    ttc_alerts_embed=[]

    # Convert alerts to text
    for t in items:
        ttc_alerts.append(t.text)
    ttc_alerts = [x.split("\n") for x in ttc_alerts if len(x)>1] 

    # Get last updated time
    lastUpdated = driver.find_element(by=By.XPATH,value = "/html/body/div[1]/main/div[2]/div/div[5]/div/div[1]/div/div/div/div/div/span[2]").text

    # footer Image
    pic = "https://cdn-icons.flaticon.com/png/512/416/premium/416739.png?token=exp=1653616579~hmac=9c3d0cac7da165e6fb02e5176add135b"
    
    # BUILD EMBEDS -----------------------------------------------

    if option == 1:  # Create embeds for all alerts
        for i in ttc_alerts:
            if len(i)>=2:
                ttc_alerts_embed.append(ttcEmbed_reg(i,pic,lastUpdated))
            else:
                ttc_alerts_embed.append(ttcEmbed_odd(i,pic,lastUpdated))
    else: # Create embed for specific bus/train 
        for i in ttc_alerts: 
            if number == i[0]:
                if len(i)>=2:
                    ttc_alerts_embed.append(ttcEmbed_reg(i,pic,lastUpdated))
                else:
                    ttc_alerts_embed.append(ttcEmbed_odd(i,pic,lastUpdated))

                break
    driver.close() #DRIVER MUST BE INSTALLED AGAIN AFTER THIS IS RAN
    return ttc_alerts_embed


# print(get_TTCStatus(URL_TTC))

# print(get_GOTrainStatus(URL_goTrain,train_xpath))

#DISCORD BOT ----------------------------------------------------------------
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
client = discord.Client()
# client =  commands.Bot(command_prefix='$',intents = intents)

load_dotenv() # Loads the .env file that resides on the same level as the script.

DISCORD_TOKEN = os.getenv("TOKEN") # Grab the API token from the .env file.


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game('Subway Surfers'))


@client.event
async def on_message(message):

    if message.author == client.user:
        return
    
    if message.content.startswith('$getTTC'):
        try:
            m = message.content.replace('$getTTC','').strip()
            await message.channel.send('🚇 Searching for TTC Service Alerts for the '+m+'...')
            ttc_delays = get_TTCStatus(URL_TTC,2,m)

            if len(ttc_delays)==0: 
                await message.channel.send('👍 No alerts for the '+m+' at the moment.')            
            else:
                for i in ttc_delays:
                    await message.channel.send(embed=i)
                    time.sleep(1)
        except NoSuchElementException:
            await message.channel.send('*Uh oh! Please try again. An error has occured.* <@601912927959777300>')

    if message.content == '$TTC':
        try:
            await message.channel.send('🚇 Searching for TTC Service Alerts... ')
            ttc_delays = get_TTCStatus(URL_TTC,1,-1)

            if len(ttc_delays)==0: 
                await message.channel.send('👍 No alerts at the moment.')
            else:
                for i in ttc_delays:
                    await message.channel.send(embed=i)
                    time.sleep(1)
        except NoSuchElementException:
            await message.channel.send('*Uh oh! Please try again. An error has occured.* <@601912927959777300>')

    if message.content == '$help':
        embed=discord.Embed(title="Transit Updates", url="https://www.ttc.ca/service-alerts", description="Need some help?", color=0xf10404)
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/1584/1584871.png")
        embed.add_field(name="$TTC", value="\n".join(["Will return all service updates.","*Ex. $TTC*"]), inline=False)
        embed.add_field(name="$getTTC [BUS # / SUBWAY LINE #]", value="\n".join(["Will return updates for a specific bus or subway line.","*Ex. $getTTC 2*"]), inline=False)
        embed.add_field(name="$GO", value="Coming Soon...", inline=False)
        embed.set_footer(text="All icons created by Freepik - Flaticon https://www.flaticon.com/free-icons")
        await message.channel.send(embed=embed)
        
client.run(DISCORD_TOKEN)