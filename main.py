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
from discord_components import DiscordComponents, ComponentsBot, Button, Select, SelectOption

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
    # print(ttc_alerts)
    # embed=discord.Embed(title="Last updated:", description="May 12, 10:29 PM", color=0xfa0000)
    # embed.set_author(name="TTC Service Alerts", url="https://www.ttc.ca/service-alerts")
    # embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/1034/1034795.png")
    # for i in ttc_alerts:
    #     if len(i)==2:
    #         embed.add_field(name=i[0], value=i[1], inline=False)
    #     else:
    #         embed.add_field(name="Other Updates...", value=i[0], inline=False)
    for i in ttc_alerts:
        if len(i)==2:
            embed=discord.Embed(title=i[0],  description=i[1], url="https://www.ttc.ca/service-alerts", color=0xff0000)
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/1034/1034795.png")
            embed.set_footer(text="https://www.ttc.ca/service-alerts")
            ttc_alerts_embed.append(embed)
        else:
            embed=discord.Embed(title="Other Updates", url="https://www.ttc.ca/service-alerts", description=i[0], color=0xff0000)
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/1034/1034795.png")
            embed.set_footer(text="https://www.ttc.ca/service-alerts")
            ttc_alerts_embed.append(embed)
    driver.close() #DRIVER MUST BE INSTALLED AGAIN AFTER THIS IS RAN
    return ttc_alerts_embed


# print(get_TTCStatus(URL_TTC))

# print(get_GOTrainStatus(URL_goTrain,train_xpath))

# Build embeds ----------------------------------------------------------------
# def setup_GOStation(updates):
#     go_embed = []
#     for alerts in updates:
#         station=alerts.split("\n")
#         info = " : ".join(station[:2])
#         descript = "\n ".join(station[2:])
#         if len(descript)>400:
#             embed=discord.Embed(title=info,  url="https://www.gotransit.com/en/trip-planning/go-service-updates#station-updates", description=descript[:400]+"...", color=0x74a42d)
#             embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/3267/3267628.png")
#             embed.set_footer(text="https://www.gotransit.com/en/trip-planning/go-service-updates#station-updates")
#             go_embed.append(embed)
#         else:
#             embed=discord.Embed(title=info,  url="https://www.gotransit.com/en/trip-planning/go-service-updates#station-updates", description=descript, color=0x74a42d)
#             embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/3267/3267628.png")
#             embed.set_footer(text="https://www.gotransit.com/en/trip-planning/go-service-updates#station-updates")
#             go_embed.append(embed)
#     return go_embed

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

def fix_textGOTrain(text):
    res = []
    for i in range(len(text)):
        if text[i] == "Delay of":
            res.append("**Delay of: **" + text[i+1])
            i=i+1
        elif text[i] == "status":
            res.append("**Status: **"+text[i+1]+"\n\n")
            i=i+1
        elif text[i].isupper(): res.append(text[i]+"\n")
        else: res.append(text[i])
    return res

def setup_GOTrain(updates):
    go_embed = []
    
    for alerts in updates:
        station=fix_textGOTrain(alerts.split("\n"))
        
        if len(station) ==2:continue
        info = " : ".join(station[:2])
        descript = "\n ".join(station[2:])
        
        embed=discord.Embed(title=info, url="https://cdn-icons.flaticon.com/png/512/2539/premium/2539414.png?token=exp=1652418832~hmac=e1052dd91732038893af861d7dab88d6", description=descript, color=0x74a42d)
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/741/741411.png")
        embed.set_footer(text="Find out more at gotransit.com/wheresmybus")
        go_embed.append(embed)
    return go_embed


# GETTING SPECIFIC TRAINS/BUSES/ETC -------------------------------------------------------------
# def specific_GOStation(updates,station):

#     go_embed=0
#     for alerts in updates:
#         stations=alerts.split("\n")
#         print(stations[0],station, station.strip() in stations[0])
#         print(type(stations[0]),type(station), len(station),len(stations[0]))

#         if stations[0] in station:
#             info = " : ".join(stations[:2])
#             descript = "\n ".join(stations[2:])
#             embed=discord.Embed(title=info,  url="https://www.gotransit.com/en/trip-planning/go-service-updates#station-updates", description=descript, color=0x74a42d)
#             embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/3267/3267628.png")
#             embed.set_footer(text="https://www.gotransit.com/en/trip-planning/go-service-updates#station-updates")
#             go_embed=embed
#     return go_embed

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
        m = message.content.replace('$getTTC','')
        await message.channel.send(m)
    

    # if message.content.startswith('$getGOStation'):
    #     station = message.content.replace('$getGOStation','')
    #     if len(station)>=20:
    #         await message.channel.send("Make sure you entered the name of the station correctly!")
    #     gostation_delays = get_GOTransitStatus(URL_goStation,station_xpath)
    #     res = specific_GOStation(gostation_delays,station)
    #     if res == 0:
    #         await message.channel.send("No Alerts!")
    #     else:
    #         await message.channel.send(embed=res)


    if message.content.startswith('$TTC'):
        await message.channel.send('Searching for TTC Service Alerts...')
        ttc_delays = get_TTCStatus(URL_TTC)
        if len(ttc_delays)==0: 
            await message.channel.send('No alerts at the moment.')
        else:
            for i in ttc_delays:
                await message.channel.send(embed=i)
                time.sleep(1)


    # if message.content.startswith('$GOStation'):
    #     await message.channel.send('Searching for GO Service Updates: GO Stations ...')
    #     # try:
    #     gostation_delays = get_GOTransitStatus(URL_goStation,station_xpath)
    #     if len(gostation_delays)==0: 
    #         await message.channel.send('No alerts at the moment.')
    #     else:
    #         embeds = setup_GOStation(gostation_delays)
    #         for i in embeds:
    #             await message.channel.send(embed=i)
    #             time.sleep(1)
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
        await message.channel.send('Searching for GO Service Updates: GO Train ...')
        # try:
        gotrain_delays = get_GOTrainStatus(URL_goTrain,train_xpath)
        print(len(gotrain_delays))
        if len(gotrain_delays)==0: 
            await message.channel.send('No alerts at the moment.')
        else:
            embeds = setup_GOTrain(gotrain_delays)
            if len(embeds) == 0: await message.channel.send("No alerts!")
            else:
                for i in embeds:
                    await message.channel.send(embed=i)
                    time.sleep(1)

client.run(DISCORD_TOKEN)