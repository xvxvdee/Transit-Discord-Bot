import requests
from bs4 import BeautifulSoup as bsoup

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

URL_goStation = "https://www.gotransit.com/en/trip-planning/go-service-updates#station-updates"
URL_goBus = "https://www.gotransit.com/en/trip-planning/go-service-updates#bus-updates"
URL_goTrain = "https://www.gotransit.com/en/trip-planning/go-service-updates#train-updates"

URL_TTC = "https://www.ttc.ca/service-alerts"

station_xpath = "//*[@id='station-updates']/div/ul"
bus_xpath="//*[@id='bus-updates']"
train_xpath="//*[@id='train-updates']/div/ul"

#GO TRANSIT ALERTS ----------------------------------------------------------
def get_GOTransitStatus(URL,xpath):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(URL)
    container = driver.find_element(by=By.XPATH, value=xpath)

    stations = []
    items = container.find_elements(by=By.TAG_NAME, value="li")
    for station in items:
        station.click()
        time.sleep(1)
        stations.append(station.text)
    driver.close()
    return stations

def get_GOTrainStatus(URL,xpath):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(URL)
    container = driver.find_element(by=By.XPATH, value=xpath)
    # delay = container.find_elements(by=By.CLASS_NAME,value="notification-content")
    # for i in delay:
    #     delay_status = i.find_elements(by=By.CLASS_NAME,value="columns small-4")
    #     print("-----")
    #     print(delay_status.text)
    #     print("-----")

    stations = []
    items = container.find_elements(by=By.TAG_NAME, value="li")
    for station in items:
        station.click()
        time.sleep(1)
        stations.append(station.text)
    driver.close()
    return stations

#TTC SERVICE ALERTS --------------------------------------------------------
def get_TTCStatus(URL):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(URL)
    items = driver.find_elements(by=By.CLASS_NAME,value ="AlertInformation_wrapperAlertItem__3nXOe")
    ttc_alerts=[]
    ttc_alerts_embed=[]

    for t in items:
        ttc_alerts.append(t.text)
        # print(t.text)
    ttc_alerts = [x.split("\n") for x in ttc_alerts if len(x)>1] 
    for i in ttc_alerts:
        embed=discord.Embed(title=i[0],  description=i[1], color=0xff0000)
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/1034/1034795.png")
        embed.set_footer(text="https://www.ttc.ca/service-alerts")
        ttc_alerts_embed.append(embed)
    driver.close() #DRIVER MUST BE INSTALLED AGAIN AFTER THIS IS RAN
    return ttc_alerts_embed


# print(get_TTCStatus(URL_TTC))

# print(get_GOTrainStatus(URL_goTrain,train_xpath))

# Build embeds ----------------------------------------------------------------
def setup_GOStation(updates):
    go_embed = []
    for alerts in updates:
        station=alerts.split("\n")
        info = " : ".join(station[:2])
        descript = "\n ".join(station[2:])
        if len(descript)>400:
            embed=discord.Embed(title=info,  url="https://www.gotransit.com/en/trip-planning/go-service-updates#station-updates", description=descript[:400]+"...", color=0x74a42d)
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/3267/3267628.png")
            embed.set_footer(text="https://www.gotransit.com/en/trip-planning/go-service-updates#station-updates")
            go_embed.append(embed)
        else:
            embed=discord.Embed(title=info,  url="https://www.gotransit.com/en/trip-planning/go-service-updates#station-updates", description=descript, color=0x74a42d)
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/3267/3267628.png")
            embed.set_footer(text="https://www.gotransit.com/en/trip-planning/go-service-updates#station-updates")
            go_embed.append(embed)
    return go_embed

def setup_GOBus(updates):
    go_embed = []
    for alerts in updates:
        station=alerts.split("\n")
        info = " : ".join(station[:2])
        descript = "\n ".join(station[2:])

        embed=discord.Embed(title=info, url="https://www.gotransit.com/en/trip-planning/go-service-updates#bus-updates", description=descript, color=0x74a42d)
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/741/741411.png")
        embed.set_footer(text="Find out more at gotransit.com/wheresmybus")
        go_embed.append(embed)
    return go_embed


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
    if message.content.startswith('$TTC'):
        await message.channel.send('Searching for TTC Service Alerts...')
        ttc_delays = get_TTCStatus(URL_TTC)
        if len(ttc_delays)==0: 
            await message.channel.send('No alerts at the moment.')
        else:
            for i in ttc_delays:
                await message.channel.send(embed=i)
                time.sleep(1)


    if message.content.startswith('$GOStation'):
        await message.channel.send('Searching for GO Service Updates: GO Stations ...')
        # try:
        gostation_delays = get_GOTransitStatus(URL_goStation,station_xpath)
        if len(gostation_delays)==0: 
            await message.channel.send('No alerts at the moment.')
        else:
            embeds = setup_GOStation(gostation_delays)
            for i in embeds:
                await message.channel.send(embed=i)
                time.sleep(1)
    # except:
        # await message.channel.send("Please try again. An error has occured :(")
    if message.content.startswith('$GOBus'):
        await message.channel.send('Searching for GO Service Updates: GO Bus ...')
        # try:
        gobus_delays = get_GOTransitStatus(URL_goBus,bus_xpath)
        if len(gobus_delays)==0: 
            await message.channel.send('No alerts at the moment.')
        else:
            embeds = setup_GOBus(gobus_delays)
            for i in embeds:
                await message.channel.send(embed=i)
                time.sleep(1)

    if message.content.startswith('$GOTrain'):
        await message.channel.send('Searching for GO Service Updates: GO Bus ...')
        # try:
        gobus_delays = get_GOTransitStatus(URL_goBus,bus_xpath)
        if len(gobus_delays)==0: 
            await message.channel.send('No alerts at the moment.')
        else:
            embeds = setup_GOBus(gobus_delays)
            for i in embeds:
                await message.channel.send(embed=i)
                time.sleep(1)

client.run(DISCORD_TOKEN)