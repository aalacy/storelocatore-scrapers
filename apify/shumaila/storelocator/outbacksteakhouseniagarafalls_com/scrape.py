#
from bs4 import BeautifulSoup
import csv
import string
import re, time
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }


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
    url = 'http://outbacksteakhouseniagarafalls.com/'
    page = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(page.text,"html.parser")
    repo_list = soup.findAll("div",{'class':'split'})
    print(len(repo_list))
    for repo in repo_list:
        try:
            coord = repo.find('iframe')
            coord = coord['src']
            #print(coord)
            start = coord.find('!2d')+3
            end = coord.find('!3d',start)
            lat = coord[start:end]
            start = end + 3
            end = coord.find('!2m',start)
            longt = coord[start:end]
            repo = repo.text
            repo = re.sub(pattern," ",repo)
            address,hours = repo.split("\n")
            hours = hours.replace("pm","pm ")
            hours = hours.replace(" Complimentary Parking on site Make Reservations","")
            hours = hours.replace(" Street Parking in front of building", "")
            address = address.lstrip()

            title,street = re.split('\d',address,1)
            
            address = address.replace(title,"")
            street,phone = re.split('•',address,1)
            phone = phone.lstrip()

            #print(street)
            street = street.replace(title,"")
            #print(title)
            title = "Outback Steakhouse " + title
            if hours.find('closed') > -1:
                hours = 'Currently Closed'
            data.append([
                'http://outbacksteakhouseniagarafalls.com/',
                'http://outbacksteakhouseniagarafalls.com/',
                title,
                street,
                'Niagara Falls',
                'Ontario',
                "<MISSING>",
                "CA",
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

