import requests
from bs4 import BeautifulSoup
import csv
import string
import re



def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    p = 0
    #shopvgs.com
    url = 'https://us.homesense.com/all-stores'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    #print(soup)
    repo_list = soup.findAll('div',{'class':'col-md-3 col-xs-3 locator-txt store-padding'})
    #print(len(repo_list))

    soup = str(soup)
    cleanr = re.compile('<.*?>')
    pattern = re.compile(r'\s\s+')
    for repo in repo_list:
        state = repo.find("h2").text
        start = state.find(",")
        city = state[0:start]
        start = start + 2
        state = state[start:len(state)]

        address = repo.find('span',{'class':'grey-txt'}).text
        address = re.sub(pattern,"|",address)

        address = address[1:len(address)-1]
        start = address.find("|")
        title = address[0:start]
        start = start + 1
        end = address.find("|",start)
        street = address[start:end]
        start = address.find(state)
        start = address.find(" ", start) + 1
        end = address.find("\n", start)
        pcode = address[start:end]
        try:
            phone = repo.find('a').text
        except:
            phone = "<MISSING>"
        try:
            hours = repo.findAll('strong')
            if len(hours) == 1:
                hours = hours[0].text
                hours = re.sub(pattern,"|",hours)
                hours = hours[1:len(hours)-1]
            else:
                hours = hours[1].text
                hours = re.sub(pattern, " ", hours)
                hours = hours[1:len(hours) - 1]
                
        except:
            hours = "<MISSING>"

        hours = hours.replace('AM',' AM ').replace('PM',' PM ')

        data.append([
            'https://us.homesense.com/',
            'https://us.homesense.com/all-stores',
            title,
            street,
            city,
            state,
            pcode,
            'US',
            "<MISSING>",
            phone,
            "<MISSING>",
            "<MISSING>",
            "<MISSING>",
            hours
        ])
        #print(p,data[p])
        p += 1



    return data


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
