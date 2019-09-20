# Import libraries
import requests
from bs4 import BeautifulSoup
import csv


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
    url = 'https://www.andalemexican.com/locations'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    # print(soup)
    repo_list = soup.findAll('div', {'class': 'summary-thumbnail-outer-container'})
    for repo in repo_list:
        detail = repo.find('a', {'class': 'summary-thumbnail-container sqs-gallery-image-container'})
        title = detail['data-title']
        descr = detail['data-description']
        start = descr.find("</p>")+7
        end = descr.find("<br />")
        address = descr[start:end]
        start = end+6
        end = descr.find("<br />",start)
        state = descr[start:end]
        start = state.find(",")
        city = state[0:start]
        state = state[start+2:len(state)]

        try:
            state, xip = state.split(" ")
        except:
            xip = "<MISSING>"
        start = descr.find("<strong>")+8
        end = descr.find("</strong>")
        phone = descr[start:end]
        start= descr.find("Hours:")+9
        start = descr.find("<",start) + 6
        end = descr.find("</p>",start)
        hours = descr[start:end]
        if hours[0] == ">":
            hours = hours[1:len(hours)]

        print(hours)
        data.append([
            url,
            title,
            address,
            city,
            state,
            xip,
            'US',
            "<MISSING>",
            phone,
            "<MISSING>",
            "<MISSING>",
            "<MISSING>",
            hours
        ])

        # print(address)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()