# Import libraries
import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(
            ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    p = 1
    url = 'https://www.romeospizza.com/locations/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    repo_list = soup.findAll('div', {'class': 'elementor-widget-container'})
    
    #print(len(repo_list))
    for repo in repo_list:
        link = repo.find('a')
        try:
            link = link['href']
            if len(link) > 3:
                page = requests.get(link)
                soup = BeautifulSoup(page.text, "html.parser")
                title = soup.find('div',{'class':'Location-Name lp-param lp-param-locationName'}).text
                #street = soup.find('div',{'class':'Address-line Address-streetOne'})
                address = soup.findAll('div',{'class':'Address-line'})
                #print(len(address))
                if len(address) == 2:
                    street = address[0].text
                    state = address[1].text
                elif len(address) == 3:
                    street = address[0].text + " " + address[1].text
                    state = address[2].text
                try:
                    phone = soup.find('span',{'class':'phone-text'}).text
                except:
                    phone = "<MISSING>"
                    
                detail = soup.findAll('tr',{'class':'hours-row'})
                hours = ""
                for det in detail:
                    hours = hours + "| "+ det.text

                map = soup.find('a',{'class':'btn btn-primary directions-cta btn-lg lp-param lp-param-routableCoordinate lp-param-getDirectionsText'})
                map = map['href']
                start = map.find("q=")
                start = start + 2
                end = map.find(",", start)
                lat = map[start:end]
                longt = map[end+1:len(map)]
                start = state.find(",")
                city = state[0:start]
                start = start + 2
                end = start + 3
                temp = state[start:end]
                pcode = state[end:len(state)]
                state = temp
                #print(link)
                #print(title)
                #print(street)
                #print(city)
                #print(state)
                #print(pcode)
                #print(phone)
                #print(lat)
                #print(longt)
                #print(hours)
                #print("...............")
                data.append([
            'https://www.romeospizza.com/',
            link,
            title,
            street,
            city,
            state,
            pcode,
            'US',
            "<MISSING>",
            phone,
            "<MISSING>",
            lat,
            longt,
            hours
        ])
                
        except:
            pass
        
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
