# Import libraries
import requests
from bs4 import BeautifulSoup
import csv
import string
import re


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    url = 'http://www.rubytuesday.com/locations'
    pnumber = 0
    done = False
    while not done:
        link = url+"?locationId=7142&start="+str(pnumber)+"&count=4"
        page = requests.get(link)
        soup = BeautifulSoup(page.text, "html.parser")
        repo_list = soup.findAll('div', {'class': 'restaurant-location-item clearfix'})
        cleanr = re.compile('<.*?>')
        pattern = re.compile(r'\s\s+')
        for repo in repo_list:
            storeId = repo.find('input', {'name': 'locationId'})['value']
            title = str(repo.find('h1'))
            address = str(repo.find('address').text)
            phone = repo.find('a')
            phone = str(phone['href'])
            phone = phone[4:len(phone)]
            thour = repo.find('table')
            trow = thour.findAll('tr', {'class': 'hourstr'})
            hours = ""
            for erow in trow:
                htd = erow.findAll('td')
                temp = " "
                for etd in htd:
                    temp = temp + " " + str(etd)
                hours =  hours + "|" + temp

            title = re.sub(cleanr,"",title)
            address = re.sub(pattern, "|", address)
            address = re.sub(cleanr, "", address)
            address = address.replace(",", "")
            start = 2
            start = address.find("|",start)
            street = address[1:start]
            end = address.find("|", start+1)
            city = address[start+1:end]
            start = end + 1
            end = address.find("|", start)
            state = address[start:end]
            pcode = address[end+1: len(address)-1]
            hours = re.sub(cleanr, "", hours)
            hours = hours[3:len(hours)]
            if phone.find("-") == -1 and phone.find(")") == -1:
                phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:10]
            if pcode.find("|") != -1:
                street = street + city
                city = state
                state = pcode[0:pcode.find("|")]
                pcode = pcode[pcode.find("|")+1 : len(pcode)]

            if len(hours) < 4:
                hours = "<MISSING>"
            if len(phone) < 3:
                phone = "<MISSING>"
            if len(state) < 2:
                state = "<MISSING>"
            if len(city) < 3:
                city = "<MISSING>"
            if len(pcode) < 5:
                pcode = "<MISSING>"
            if len(title) < 4:
                title = "<MISSING>"

            latlng = repo.find('div', {'class': 'map_info clearfix'})
            lat = latlng['data-lat']
            lng = latlng['data-lng']
            
            data.append([
                url,
                '<MISSING>',
                title,
                street,
                city,
                state,
                pcode,
                "US",
                storeId,
                phone,
                "<MISSING>",
                lat,
                lng,
                hours
              ])

        if len(repo_list) == 0:
            done = True
        else:
            pnumber += 4
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
