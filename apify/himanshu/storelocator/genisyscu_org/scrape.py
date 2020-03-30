import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = locator_domain = "https://www.genisyscu.org"
    country_code = "US"
    store_number = "<MISSING>"
    r = session.get("https://www.genisyscu.org/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    # print(soup.prettify())
    return_main_object = []
    addresses = []
    # links = []
    for location in soup.find("section",{'class':"inside"}).find_all('ul'):
        # print(location.find("a")["href"])
        for li in location.find_all('li'):
            page_url= base_url + li.a['href']
            location_name = li.a.text.strip()
            location_type = "ATMs And Credit Union"
            address = li.find('span',{'itemprop':'streetAddress'})


            if address != None:
                list_address = list(address.stripped_strings)
                list_address = [el.replace('\xa0',' ') for el in list_address]
                street_address = list_address[0].strip()
                city = list_address[-1].split(',')[0].strip()
                state = list_address[-1].split(',')[1].split()[0].strip()
                zipp = list_address[-1].split(',')[1].split()[-1].strip()
                phone_tag = li.find('span',{'itemprop':'telephone'}).text.strip()
                phone = "(" +re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_tag))[0].replace('\xa0','').strip()

                r_loc = session.get(page_url,headers = headers)
                soup_loc = BeautifulSoup(r_loc.text,'lxml')
                section = soup_loc.find('section',{'class':'inside'}).find('article')
                table = section .find('table')
                h= []
                for time in table.find_all('time',{'itemprop':'openingHours'}):
                    hours =  time.text.replace('\n',' ').strip()
                    h.append(hours)
                if len(" ".join(h).split('Friday Drive')) ==1:
                    hours_of_operation = " ".join(h).split('Friday Drive')[0].replace('(','').strip().split('*')[0].strip().split('Contac')[0].strip()
                else:

                    hours_of_operation =" ".join(h).split('Friday Drive')[0].replace('(','').strip()+ " "+ " ".join(h).split('Friday Drive')[-1].split(')')[-1].strip().replace('521-8440 x5','').replace('*shared branching lobby only.','').strip()
                latitude =section.find('iframe')['src'].split('1d')[1].split('!3d')[0].split('!2d')[0].split('.')[0][-2:].strip() +"." +section.find('iframe')['src'].split('1d')[1].split('!3d')[0].split('!2d')[0].split('.')[1].strip()
                longitude = section.find('iframe')['src'].split('1d')[1].split('!3d')[0].split('!2d')[-1]

            else:
                #it's all for online
                phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(li.text.strip()))[0]
                street_address = "<MISSING>"
                city = "<MISSING>"
                state = "<MISSING>"
                zipp = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                hours_of_operation = "<MISSING>"
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
            store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
            store = [x if x.replace('\xa0',' ')  else "<MISSING>" for x in store]

            if store[2] in addresses:
                continue
            addresses.append(store[2])

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
