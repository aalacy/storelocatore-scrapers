import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time

DOMAIN = 'https://www.biglots.com'
MISSING = '<MISSING>'

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
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    data=[]
    url = "https://local.biglots.com/sitemap.xml"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    loc_url = soup.findAll('xhtml:link', href = True)
    for l in loc_url:
        try:
            if len(re.split('/', l['href'])) >=6:
                page_url = l['href']
                res = requests.get(page_url)
                l_soup = BeautifulSoup(res.content, "html.parser")
                location_name = l_soup.find('h1', attrs = {'class':'Hero-title'}).text.strip()
                street_address = l_soup.find('span', attrs = {'class':'c-address-street-1'}).text.strip()
                city = l_soup.find('span', attrs = {'class':'c-address-city'}).text.strip()
                state_ab = l_soup.find('span', attrs = {'class':'c-address-state'}).text.strip()
                state = us_state_abbrev[state_ab]
                zipcode = l_soup.find('span', attrs = {'class':'c-address-postal-code'}).text.strip()
                phone = l_soup.find('div', attrs = {'class':'Phone-display Phone-display--withLink'}).text.strip()
                lat = l_soup.find('span', attrs = {'class':'c-js-distance-container'})['data-latitude']
                lon = l_soup.find('span', attrs = {'class':'c-js-distance-container'})['data-longitude']
                store_number = l_soup.find('button', attrs = {'class':'Hero-button js-favorite-store'})['value']
                hrs = l_soup.findAll('tr', attrs = {'itemprop':'openingHours'})
                hours_of_operation = ''
                for h in  hrs:
                    if h['content']:
                        hours_of_operation = hours_of_operation + h['content'] + ',' 
                location_type = MISSING
                data.append([DOMAIN, page_url, location_name, street_address, city, state, zipcode, 'US', store_number, phone, location_type, lat, lon, hours_of_operation])
        except requests.exceptions.RequestException:
            pass
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
