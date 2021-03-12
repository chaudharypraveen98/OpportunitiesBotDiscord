import os
import random

import discord
import requests
from keep_alive import keep_alive
from replit import db
from requests_html import HTML

client = discord.Client()


# It will request the url and get the response body and status code
def url_to_text(url):
    r = requests.get(url)
    if r.status_code == 200:
        html_text = r.text
        return html_text


# It will parse the html data into structure way
def pharse_and_extract(url, name=2020):
    html_text = url_to_text(url)
    if html_text is None:
        return ""
    r_html = HTML(html=html_text)
    return r_html


# it will loop through all the internship and extract valuable data
def get_internship(url):
    internships = []
    res_data = pharse_and_extract(url)
    opportunties = res_data.find(".individual_internship")
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


# It will extract the freelancing opportunities
def extract_from_freelancer(res_html):
    freelance_works = []
    opportunities = res_html.find(".JobSearchCard-item")
    for opportunity in opportunities:
        title = opportunity.find(".JobSearchCard-primary-heading a", first=True).text
        freelance_link = opportunity.find(".JobSearchCard-primary-heading a", first=True).attrs['href']
        avg = opportunity.find(".JobSearchCard-primary-price")
        if avg:
            avg_proposal = avg[0].text
        else:
            avg_proposal = "Not mentioned"
        apply_lastes_by = opportunity.find(".JobSearchCard-primary-heading-days", first=True).text
        desc = opportunity.find(".JobSearchCard-primary-description", first=True).text
        freelance_works.append({
            'title': title,
            'description': desc,
            'apply_lastes_by': apply_lastes_by,
            'avg_proposal': avg_proposal,
            'freelance_link': f"https://www.freelancer.com/{freelance_link}"
        })
    return freelance_works


# Starter function for freelancing function
def get_freelance(keyword=None):
    random_keywords = ['python', 'java', 'web', 'javascript', 'graphics']
    if keyword:
        url = f"https://www.freelancer.com/jobs/?keyword={keyword}"
    else:
        random_keyword = random.choice(random_keywords)
        url = f"https://www.freelancer.com/jobs/?keyword={random_keyword}"
    res_html = pharse_and_extract(url)
    freelance_works = extract_from_freelancer(res_html)
    return freelance_works


# It will start the scraper. If It has a keyword then url will be based upon that.
def start_scraper(keyword=None):
    if keyword:
        url = f"https://internshala.com/internships/keywords-{keyword}"
    else:
        url = "https://internshala.com/internships"
    return get_internship(url)


# Simple Formatter for discord messages
def format_message(message):
    formatted_message = ""
    for i in message:
        formatted_message += f"{i.upper()}  --> {message[i]}\n"
    return formatted_message


@client.event
async def on_ready():
    # text_channel_list = []
    # for server in client.servers:
    #     for channel in server.channels:
    #         if channel.type == 'Text':
    #             text_channel_list.append(channel)
    # print(text_channel_list)
    channel = client.get_channel(793734648224022558)
    print("We have logged in as", client.user)
    # await channel.send("I am back")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('$hello'):
        await message.channel.send(f"Hello {message.author}")
    if message.content.startswith('$reset internship'):
        del db['internship']
        await message.channel.send("cleared internship")
    if message.content.startswith('$reset freelance'):
        del db['freelance']
        await message.channel.send("cleared freelance")
    if message.content.startswith('$reset'):
        db.clear()
        await message.channel.send("cleared all")
    if message.content.startswith('$help'):
        db.clear()
        await message.channel.send(
            "------------------\nwrite $internship with space separated field or keyword \n\nExample \n$internship python \n\nFor Freelance \n----------------------\nwrite $freelance with space separated\n----------------------- \n\nExample \n$freelance python \n\nOr \n\n $freelance \nfor random freelance work")

    if message.content.startswith('$internship'):
        keyword = message.content.split(" ")[-1]
        print(keyword)
        if 'internship' in db.keys():
            if keyword in db['internship'].keys():
                result = random.choice(db[keyword])
            else:
                opportunities = start_scraper(keyword=keyword)
                db['internship'][keyword] = opportunities
                result = random.choice(opportunities)
        else:
            db['internship'] = {}
            opportunities = start_scraper(keyword=keyword)
            db['internship'][keyword] = opportunities
            result = random.choice(opportunities)

        result_message = format_message(result)
        await message.channel.send(result_message)

    if message.content.startswith('$freelance'):
        key_list = message.content.split(" ")
        if len(key_list) > 1:
            keyword = key_list[1]
            if 'freelance' in db.keys():
                if keyword in db['freelance'].keys():
                    free_result = random.choice(db['freelance'][keyword])

                else:
                    freelance_works = get_freelance(keyword=keyword)
                    db['freelance'][keyword] = freelance_works
                    free_result = random.choice(freelance_works)

            else:
                db['freelance'] = {}
                freelance_works = get_freelance(keyword=keyword)
                db['freelance'][keyword] = freelance_works
                free_result = random.choice(freelance_works)
            result_message = format_message(free_result)
            await message.channel.send(result_message)

        else:
            if 'freelance' in db.keys():
                if 'random' in db['freelance'].keys():
                    free_result = random.choice(db['freelance']['random'])
                else:
                    data = get_freelance()
                    db['freelance']['random'] = data
                    free_result = random.choice(data)
            else:
                db['freelance'] = {}
                data = get_freelance()
                db['freelance']['random'] = data
                free_result = random.choice(data)

            result_message = format_message(free_result)
            await message.channel.send(result_message)

# For making server alive all the time
keep_alive()

client.run(os.getenv('TOKEN'))
