#
import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select


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

    pattern = re.compile(r'\s\s+')
    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

    total = 0
    for i in range(0,len(states)):
        p = 0
        url = 'https://www.abcsupply.com/locations/location-results'
        #print(states[i])
        result = requests.get(url, data={'State': states[i]})
        #time.sleep(1)
        soup = BeautifulSoup(result.text,"html.parser")
        hoursd = soup.findAll('ul',{'class':'dropdown-menu'})
        links = soup.findAll('div',{'class':'location-name'})
        #print(result.text)
        result = result.text
        start = 0
        
        flag = True
        try:
            counr = soup.find('div',{'class':'rcount'}).find('strong').text
            total = total + int(counr)
            #print(states[i],counr, total)
        except:
            pass
        
        
        while flag:
            start = result.find(" var marker = new google.maps.Marker",start)
            if start == -1:
                flag = False
            else:
                start = result.find("lat:", start)
                start = result.find(":", start)+2
                end = result.find(",", start)
                lat = result[start:end]
                start = end
                start = result.find("lng:", start)
                start = result.find(":", start) + 2
                end = result.find("}", start)
                longt = result[start:end]

                link = links[p].find('a')
                link = "https://www.abcsupply.com" +link['href']
                start = result.find("BranchNumber", end)
                start = result.find("=", start) +1
                end = result.find('"', start)
                store = result[start:end]
                start = result.find(">", end)+1
                end = result.find("<", start)
                title = result[start:end]
                start = result.find("location-address",end)
                start = result.find("+", start) + 1
                start = result.find("'", start) + 1
                end = result.find('<', start)
                street = result[start:end]
                start = result.find("+", end) + 1
                start = result.find("'", start) + 1
                end = result.find('<', start)
                address = result[start:end]
                city,address = address.split(", ")
                state,pcode = address.split(" ")
                start = result.find("tel", end) + 1
                start = result.find(">", start) + 2
                end = result.find('<', start)
                phone = result[start:end]
                start = end
                hours = hoursd[p].text
                hours = re.sub(pattern," ",hours)
                hours = hours.replace('Branch Hours','')
                hours = hours.lstrip()
                if len(hours) < 3:
                    hours = "<MISSING>"
                print([
                    'https://www.abcsupply.com/',
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    store,
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
                    hours
                ])
                data.append([
                    'https://www.abcsupply.com/',
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    store,
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
                    hours
                ])
                p+=1
                
        
        



        print("............................")
    print(total)
    return data

def scrape():
    data = fetch_data()
    write_output(data)


scrape()

