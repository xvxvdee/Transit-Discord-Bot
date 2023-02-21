
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
URL_GRT = "https://www.grt.ca/en/service-updates/service-alerts.aspx"

station_xpath = "//*[@id='station-updates']/div/ul"
bus_xpath="//*[@id='bus-updates']"
train_xpath="//*[@id='train-updates']/div/ul"

#EMBEDS HELPERS --------------------------------------------------------

def Embed_reg(data, pic,lastUpdated, link, option): # Create embed for alerts with bus/train number 
    if option == 0:
        embed=discord.Embed(title=data[0],  description=" ".join(data[1:]), url=link, color=0xff0000)
        embed.set_thumbnail(url=pic)
        embed.add_field(name="Last updated", value=lastUpdated, inline=False)
        embed.set_footer(text=link)
        return embed
    else:
        embed=discord.Embed(title=data[0],  description=" ".join(data[1:]), url=link, color=0x0079DD)
        embed.set_thumbnail(url=pic)
        embed.set_footer(text=link)
        return embed


def Embed_odd(data,pic,lastUpdated, link, option): # Create embed for other alerts
    if option == 0:
        embed=discord.Embed(title="Other Updates", url=link, description=data[0], color=0xff0000)
        embed.set_thumbnail(url=pic)
        embed.add_field(name="Last updated", value=lastUpdated, inline=False)
        embed.set_footer(text=link)
        return embed
    else:
        embed=discord.Embed(title="Other Updates", url=link, description=data[0],  color=0x0079DD)
        embed.set_thumbnail(url=pic)
        embed.set_footer(text=link)
        return embed



#TTC SERVICE ALERTS --------------------------------------------------------
def get_TTCStatus(URL,option,number):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome()
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

    # icon Image
    icon_ttc = "https://cdn-icons-png.flaticon.com/512/5348/5348561.png"
    
    link_ttc = URL_TTC
    
    # BUILD EMBEDS -----------------------------------------------

    if option == 1:  # Create embeds for all alerts
        for i in ttc_alerts:
            if len(i)>=2:
                ttc_alerts_embed.append(Embed_reg(i,icon_ttc,lastUpdated,link_ttc,0))
            else:
                ttc_alerts_embed.append(Embed_odd(i,icon_ttc,lastUpdated,link_ttc,0))
    else: # Create embed for specific bus/train 
        for i in ttc_alerts: 
            if number == i[0]:
                if len(i)>=2:
                    ttc_alerts_embed.append(Embed_reg(i,icon_ttc,lastUpdated,link_ttc,0))
                else:
                    ttc_alerts_embed.append(Embed_odd(i,icon_ttc,lastUpdated,link_ttc,0))
                break
    driver.close() #DRIVER MUST BE INSTALLED AGAIN AFTER THIS IS RAN
    return ttc_alerts_embed


# GRT ALERTS -----------------------------------------------------------------

def get_GRTStatus(URL):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome()
    driver.get(URL)

    # Select all alerts
    items = driver.find_elements(by=By.CLASS_NAME,value ="grt-alerts-item")
    grt_alerts = [i.text.split("\n") for i in items]

    print(grt_alerts)

     # icon Image
    icon_grt = "https://cdn-icons-png.flaticon.com/512/829/829378.png"
    
    link_grt = URL_GRT
    
    # BUILD EMBEDS -----------------------------------------------
    grt_alerts_embed = []
    for i in grt_alerts:
        if len(i)>=2:
            grt_alerts_embed.append(Embed_reg(i,icon_grt," ",link_grt,1))
        else:
            grt_alerts_embed.append(Embed_odd(i,icon_grt," ",link_grt,1))

    driver.close() #DRIVER MUST BE INSTALLED AGAIN AFTER THIS IS RAN
    return grt_alerts_embed
     

# print(get_TTCStatus(URL_TTC))

# print(get_GOTrainStatus(URL_goTrain,train_xpath))

#DISCORD BOT ----------------------------------------------------------------
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True
client = commands.Bot(command_prefix='$',intents = intents)

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
        print("here")
        try:
            m = message.content.replace('$getTTC','').strip()
            if not m.isalnum():
                await message.channel.send('⚠️ Please enter a bus/train route.')   
                return
            await message.channel.send('🚇 Searching for TTC Service Alerts for the '+m+'...')
            ttc_delays = get_TTCStatus(URL_TTC,2,m)
            if len(ttc_delays)==0: 
                await message.channel.send('👍 No alerts for the '+m+' at the moment.')            
            else:
                for i in ttc_delays:
                    await message.channel.send(embed=i)
                    time.sleep(1)
        except NoSuchElementException :
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

    if message.content == '$GRT':
        try:
            await message.channel.send('🚇 Searching for GRT Service Alerts... ')
            grt_delays = get_GRTStatus(URL_GRT)

            if len(grt_delays)==0: 
                await message.channel.send('👍 No alerts at the moment.')
            else:
                for i in grt_delays:
                    await message.channel.send(embed=i)
                    time.sleep(1)

        except NoSuchElementException:
            await message.channel.send('*Uh oh! Please try again. An error has occured.* <@601912927959777300>')

    if message.content == '$help':
        print("here")
        embed=discord.Embed(title="Transit Updates", url="https://www.ttc.ca/service-alerts", description="Need some help?", color=0xf10404)
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/1584/1584871.png")
        embed.add_field(name="$TTC", value="\n".join(["Will return all service updates.","*Ex. $TTC*"]), inline=False)
        embed.add_field(name="$getTTC [BUS # / SUBWAY LINE #]", value="\n".join(["Will return updates for a specific bus or subway line.","*Ex. $getTTC 2*"]), inline=False)
        embed.add_field(name="$GRT", value="\n".join(["Will return all service updates.","*Ex. $GRT*"]), inline=False)
        embed.add_field(name="$GO", value="Coming Soon...", inline=False)
        embed.set_footer(text="All icons created by Freepik - Flaticon https://www.flaticon.com/free-icons")
        await message.channel.send(embed=embed)
        
client.run(DISCORD_TOKEN)