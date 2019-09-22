# Import libraries
import xml
import lxml
import requests
from bs4 import BeautifulSoup
import csv
import string
import re


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    url = 'https://www.masseyspizza.com/locations/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    # print(soup)
    repo_list = soup.findAll('div', {'class': 'et_pb_text_inner'})
    cleanr = re.compile('<.*?>')
    state = ""
    for repo in repo_list:
        repo = str(repo)
        start = repo.find("<p>") + 3
        end = repo.find("<br", start)
        title = repo[start:end]
        # title = re.sub(cleanr, '', title)

        if title.find("strong") > -1 and title.find("NOW OPEN") == -1:
            title = re.sub(cleanr, '', title)
            print(title)
            start = end + 6
            end = repo.find("<br", start)
            address = repo[start:end]
            print(address)
            start = end + 6
            start = repo.find(">", start)+1
            end = repo.find("<", start)
            phone = repo[start:end]
            phone = re.sub("\n","",phone)
            if len(phone) == 0:
                phone = "<MISSING>"
            print(phone)
            start = repo.find("<br", end) + 6
            end = repo.find("<", start)
            hours = repo[start:end]
            start =end + 6
            end = repo.find("<", start)
            hours = hours+ " " + repo[start:end]
            print(hours)
            start = repo.find("href", end)
            start = repo.find("@", start) + 1
            if start > 0:
                end = repo.find(",", start)
                lat = repo[start:end]
                start = end+1
                end = repo.find(",", start)
                longt = repo[start:end]
            else:
                lat = "<MISSING>"
                longt = "<MISSING>"

            print(lat)
            print(longt)
            print(state)
            print(".....................")
            data.append([
                url,
                title,
                address,
                title,
                state,
                '<MISSING>',
                'US',
                '<MISSING>',
                phone,
                '<MISSING>',
                lat,
                longt,
                hours
            ])
        else:
            start = repo.find("<h3>") + 6
            if start > 0:
                start = repo.find(";",start) + 3
                end = repo.find("<", start)
                state = repo[start:end]
                if state.find("Bar") > 1:
                    state = "<MISSING>"

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
