import discord
import os
import requests
import random
from requests_html import HTML
from replit import db

client = discord.Client()


# It will request the url and get the response body and status code
def url_to_text(url):
    r = requests.get(url)
    if r.status_code == 200:
        html_text = r.text
        return html_text


# It will parse the html data into structure way and find the internship container
def pharse_and_extract(url, name=2020):
    html_text = url_to_text(url)
    if html_text is None:
        return ""
    r_html = HTML(html=html_text)
    opportunities = r_html.find(".individual_internship")
    return opportunities


# it will loop through all the internship and extract valuable data
def get_internship(url):
    internships = []
    opportunties = pharse_and_extract(url)
    for opportunity in opportunties:
        title = opportunity.find(".company a", first=True).text
        internship_link = opportunity.find(".profile a", first=True).attrs['href']
        organisation = opportunity.find(".company .company_name", first=True).text
        organisation_internships = opportunity.find(".company_name a", first=True).attrs['href']
        location = opportunity.find(".location_link", first=True).text
        start_data = opportunity.find("#start-date-first", first=True).text.split("\xa0immediately")[-1]
        ctc = opportunity.find(".stipend", first=True).text
        apply_lastes_by = opportunity.xpath(".//span[contains(text(),'Apply By')]/../../div[@class='item_body']",
                                            first=True).text
        duration = opportunity.xpath(".//span[contains(text(),'Duration')]/../../div[@class='item_body']",
                                     first=True).text
        internships.append({
            'title': title,
            'organisation': organisation,
            'location': location,
            'start_data': start_data,
            'ctc': ctc,
            'apply_lastes_by': apply_lastes_by,
            'duration': duration,
            'organisation_internships': f"https://internshala.com{organisation_internships}",
            'internship_link': f"https://internshala.com{internship_link}"
        })
    return internships


# It will start the scraper. If It has a keyword then url will be based upon that.
def start_scraper(keyword=None):
    if keyword:
        url = f"https://internshala.com/internships/keywords-{keyword}"
    else:
        url = "https://internshala.com/internships"
    return get_internship(url)


def format_message(message):
    formatted_message = ""
    for i in message:
        formatted_message += f"{i.upper()}  --> {message[i]}\n"
    return formatted_message


@client.event
async def on_ready():
    print("We have logged in as", client.user)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('$hello'):
        await message.channel.send(f"Hello {message.author}")
    if message.content.startswith('$internship reset'):
        db.clear()
        await message.channel.send("cleared all")
    if message.content.startswith('$help'):
        db.clear()
        await message.channel.send(
            "write $internship with space separated field or keyword \n Example \n$internship python")

    if message.content.startswith('$internship'):
        keyword = message.content.split(" ")[-1]
        print(keyword)
        if keyword in db.keys():
            if db[keyword]:
                result = format_message(random.choice(db[keyword]))
                await message.channel.send(result)
        else:
            opportunities = start_scraper(keyword=keyword)
            db[keyword] = opportunities
            result = format_message(random.choice(opportunities))
            await message.channel.send(result)


client.run(os.getenv('TOKEN'))
