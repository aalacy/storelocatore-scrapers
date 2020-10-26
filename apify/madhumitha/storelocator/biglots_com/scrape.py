import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
session = SgRequests()
import requests
us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Palau': 'PW',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY',
}

def write_output(data):
    with open('data.csv', mode='w', encoding='utf-8', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []
    soup = bs( requests.get("https://local.biglots.com/sitemap.xml").text, "lxml")

    for l in soup.find_all('xhtml:link', href = True):
        
            if l['href'].count("/") >= 5 and "holiday" not in l['href']:
                page_url = l['href']
                l_soup = bs(requests.get(page_url).text, "lxml")
                
                location_name = l_soup.find('h1', attrs = {'class':'Hero-title'}).text.strip()
                
                street_address = l_soup.find('span', attrs = {'class':'c-address-street-1'}).text.strip()
                
                city = l_soup.find('span', attrs = {'class':'c-address-city'}).text.strip()
                
                state_ab = l_soup.find('span', attrs = {'class':'c-address-state'}).text.strip()
                
                if len(state_ab) == 2:
                    state = state_ab
                else:
                    state = us_state_abbrev[state_ab]
                
                zipp = l_soup.find('span', attrs = {'class':'c-address-postal-code'}).text.strip()
                
                phone = l_soup.find('div', attrs = {'class':'Phone-display Phone-display--withLink'}).text.strip()
                
                lat = l_soup.find('span', attrs = {'class':'c-js-distance-container'})['data-latitude']
                
                lng = l_soup.find('span', attrs = {'class':'c-js-distance-container'})['data-longitude']
                
                store_number = l_soup.find('button', attrs = {'class':'Hero-button js-favorite-store'})['value']
                
                hrs = l_soup.findAll('tr', attrs = {'itemprop':'openingHours'})
                
                hours_of_operation = ''
                for h in  hrs:
                    if h['content']:
                        hours_of_operation = hours_of_operation + h['content'] + ',' 
               
                
                
                store = []
                store.append("https://www.biglots.com")
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append("US")
                store.append(store_number)
                store.append(phone)
                store.append('<MISSING>')
                store.append(lat)
                store.append(lng)
                store.append(hours_of_operation)
                store.append(page_url)
                
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
               
                yield store
       
   

def scrape():
    data = fetch_data()
    write_output(data)

scrape()