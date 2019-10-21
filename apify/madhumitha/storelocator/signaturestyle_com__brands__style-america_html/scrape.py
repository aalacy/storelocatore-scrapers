import csv
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

DOMAIN = 'https://www.signaturestyle.com'
MISSING = '<MISSING>'

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)
    data_df = pd.read_csv("data.csv")
    data_df.drop_duplicates(subset ="store_number", keep = False, inplace = True)
    data_df.drop_duplicates(subset ="street_address", keep = False, inplace = True)
    data_df.to_csv('data.csv', index=False)

def fetch_data():
    data=[]
    url = "https://www.signaturestyle.com/salon-directory.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    loc_url = soup.findAll('a', attrs = {'class':'btn btn-primary'})
    for l in loc_url:
        try:
            if 'pr' not in l['href']:
                loc_url = DOMAIN + l['href']
                loc_res = requests.get(loc_url)
                loc_soup = BeautifulSoup(loc_res.content, "html.parser")
                loc_tag = loc_soup.findAll('td')
                for loc in loc_tag:
                    if loc.find('a', href = True) is not None:
                        page_url = DOMAIN + loc.find('a', href = True)['href']
                        store_number = re.findall('\d+',page_url)[-1]
                        page_res = requests.get(page_url)
                        page_soup = BeautifulSoup(page_res.content, "html.parser")
                        if page_soup.find('h2', attrs = {'class':'hidden-xs salontitle_salonlrgtxt'}) is None:
                            continue
                        location_name = page_soup.find('h2', attrs = {'class':'hidden-xs salontitle_salonlrgtxt'}).text.strip()
                        phone = page_soup.find('a', attrs = {'id':'sdp-phone'}).text.strip()
                        street_address = page_soup.find('span', attrs = {'itemprop':'streetAddress'}).text.strip()
                        city = page_soup.find('span', attrs = {'itemprop':'addressLocality'}).text.strip()
                        state = page_soup.find('span', attrs = {'itemprop':'addressRegion'}).text.strip()
                        zipcode = page_soup.find('span', attrs = {'itemprop':'postalCode'}).text.strip()
                        if(len(zipcode) <= 4):
                            zero = 5 - len(zipcode)
                            for z in str(zero):
                                zipcode = str(0) + zipcode
                        if len(zipcode) == 5:
                            country = 'US'
                        else:
                            country = 'CA'
                        hrs = page_soup.find('div', attrs = {'class':'salon-timings'}).text.strip()
                        hours_of_operation = re.sub('\n+', ' ', hrs)
                        if hours_of_operation == '':
                            hours_of_operation = MISSING
                        loc_map =  page_soup.find('div', attrs = {'class' : 'salondetailspagelocationcomp'})
                        loc_tag = loc_map.find('script', attrs = {'type':'text/javascript'}).text.strip()
                        latlng = re.findall('[-+]?[0-9]*\.?[0-9]+', loc_tag)
                        lat = latlng[-2].strip()
                        location_type = MISSING
                        data.append([DOMAIN, page_url, location_name, street_address, city, state, zipcode, country, store_number, phone, location_type, lat, lon, hours_of_operation])
        except requests.exceptions.RequestException:
            pass
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
