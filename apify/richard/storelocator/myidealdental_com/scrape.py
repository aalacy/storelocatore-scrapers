from bs4 import BeautifulSoup
import csv
import string
import re, time
import json
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

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
    output = []
    
    url = 'https://www.myidealdental.com/locations/'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser") 
    divlist = soup.find('div',{'class':'locations-list-wrapper'}).findAll('li', {'class': 'locations-list-item'})
    # print("states = ",len(divlist))
    p = 0
    for div in divlist:
        link = div.find('div', {'class': 'location-links'}).find('a')['href']
        r = session.get(link, headers=headers, verify=False)
        r = r.text.split('<script type="application/ld+json">',1)[1].split('</script>')[0]
        data = json.loads(r)
        location_id = div['data-office-id']

            # Type
        location_type = "<MISSING>"

            # Name
        location_title = data['name']

            # Street
        street_address = data['address']['streetAddress']
        # print(street_address)

            # city
        city = data['address']['addressLocality']

            # zip
        zipcode = data['address']['postalCode']

            # State
        state = data['address']['addressRegion']

            # Phone
        phone = data['telephone']
        phone = data['telephone'][0:3] + '-' + data['telephone'][3:6]+ '-' + data['telephone'][6:len(data['telephone'])]
        phone = phone.replace("--","-")
        

            # Lat
        lat = data['geo']['latitude']

            # Long
        lon = data['geo']['longitude']


        hours_of_operation = ""
        raw_hours = data['openingHoursSpecification']
        for hours in raw_hours:
            day = hours['dayOfWeek']
            if len(day[0]) != 1:
                day = ' '.join(hours['dayOfWeek'])
            try:
                opens = hours['opens']
                closes = hours['closes']
                if opens != "" and closes != "":
                    clean_hours = day + " " + opens + "-" + closes
            except:
                clean_hours = day + " Closed"
            hours_of_operation = (hours_of_operation + " " + clean_hours).strip()

        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

        output.append([
                        'https://www.myidealdental.com/',
                        link,
                        location_title,
                        street_address,
                        city,
                        state,
                        zipcode,
                        "US",
                        location_id ,
                        phone,
                        location_type,
                        lat,
                        lon,
                        hours_of_operation
                    ])
        #print(p,output[p])
        p += 1

        
    
                
            
        
    return output


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
