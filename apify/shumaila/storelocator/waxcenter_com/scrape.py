#
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

    pattern = re.compile(r'\s\s+')

    p = 0
    url = 'https://www.waxcenter.com/locations/search-by-state'
    page = requests.get(url)
    soup = BeautifulSoup(page.text,"html.parser")
    repo_list = soup.findAll("a",{'class':'search-results-name'})
    for repo in repo_list:
        print(repo.text)
        statelink = "https://www.waxcenter.com" + repo['href']
        page1 = requests.get(statelink)
        soup1 = BeautifulSoup(page1.text,"html.parser")
        link_list = soup1.findAll("h3", {'class': 'search-results-name'})
        for link in link_list:
            link = link.find('a')
            print(link.text)
            if link.text.find("Opening Soon") == - 1 and link.text.find("Closed") == - 1:
                link = "https://www.waxcenter.com" + link['href']
                page2 = requests.get(link)
                soup2 = BeautifulSoup(page2.text, "html.parser")
                title = soup2.find('h1',{'class':'title'}).text
                phone = soup2.find('span', {'class': 'phoneNumber'}).text
                hours = soup2.find('div', {'class': 'center-hours'}).text
                script = soup2.find('script',{'type':'application/ld+json'})
                script = str(script)
                start = script.find('"addressRegion"')
                start = script.find(':',start)
                start = script.find('"', start)+1
                end = script.find('"', start)
                state = script[start:end]
                start = script.find('"postalCode"')
                start = script.find(':', start)
                start = script.find('"', start) + 1
                end = script.find('"', start) 
                pcode = script[start:end]
                start = script.find('"streetAddress"')
                start = script.find(':', start)
                start = script.find('"', start) + 1
                end = script.find('"', start) 
                street = script[start:end]
                start = script.find('"addressLocality"')
                start = script.find(':', start)
                start = script.find('"', start) + 1
                end = script.find('"', start) 
                city = script[start:end]
                start = script.find('"latitude"')
                start = script.find(':', start)
                start = script.find('"', start) + 1
                end = script.find('"', start)
                lat = script[start:end]
                start = script.find('"longitude"')
                start = script.find(':', start)
                start = script.find('"', start) + 1
                end = script.find('"', start) 
                longt = script[start:end]
                hours = re.sub(pattern, " ", hours)
                hours = hours.replace("AM", " AM ")
                hours = hours.replace("PM", " PM ")
                hours = hours.replace("-", " - ")
                hours = hours.replace("  ", " ")
                start = link.find('-')
                state = link[start-2:start]
                state = state.upper()
                if len(hours) < 5:
                    hours = "<MISSING>"
                if len(phone) < 5:
                    phone = "<MISSING>"
                if len(lat) < 4:
                    lat = "<MISSING>"
                if len(longt) < 4:
                    longt = "<MISSING>"
                if len(pcode) < 4:
                    pcode = "<MISSING>"
                if len(state) < 2:
                    state = "<MISSING>"
                if len(city) < 4:
                    city = "<MISSING>"

               
                data.append([
                    'https://www.waxcenter.com/',
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    "<MISSING>",
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
                    hours
                ])
                p += 1


    print(len(data))
    return data

def scrape():
    data = fetch_data()
    write_output(data)


scrape()

