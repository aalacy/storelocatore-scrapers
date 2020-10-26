import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress
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
    data = []
    
    url = 'https://blackfinnameripub.com/locations/'
    r = session.get(url, headers=headers, verify=False)
  
    soup =BeautifulSoup(r.text, "html.parser")
   
    link_list = soup.findAll('a', {'class': 'location_btn'})
    repo_list = soup.findAll('div', {'class': 'location_content'})
    print("states = ",len(link_list))
    p = 0
    for repo in repo_list:
        store = repo['id']
        store = store.replace('location_','')
        #print(store)
        link = ''
        for j in range(0,len(link_list)):
            
            if store ==  link_list[j]['id']:
                link = link_list[j]['ref']
                title =link_list[j].text
                
                address = repo.find('div', {'class': 'location_address'})
                
                phone = address.findAll('p')
                phone = phone[1].text
                phone = phone.replace('\n','')
                phone = phone.replace('.','-')
                temp = address.find('span').text
                print(temp)
                address = address.find('input')
                if len(temp) < 2:                    
                    address = address['value']
                else:
                    address =temp +', ' + address['value']
                
                hours = repo.find('div', {'class': 'location_hours'}).text
                hours = hours.replace('\n',' ')
                hours = hours.replace('Hours of Operations','')
                hours = hours.lstrip()
                #print(address)
                address = address.replace('\n',' ')
                address = address.lstrip()
                address = usaddress.parse(address)
                i = 0
                street = ""
                city = ""
                state = ""
                pcode = ""
                while i < len(address):
                    temp = address[i]
                    if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or \
                            temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find(
                            "USPSBoxID") != -1:
                        street = street + " " + temp[0]
                    if temp[1].find("PlaceName") != -1:
                        city = city + " " + temp[0]
                    if temp[1].find("StateName") != -1:
                        state = state + " " + temp[0]
                    if temp[1].find("ZipCode") != -1:
                        pcode = pcode + " " + temp[0]
                    i += 1
                city = city.lstrip()
                city = city.replace(",",'')
                #street = street.replace(",",'')
                street = street.lstrip()
                state = state.lstrip()
                pcode = pcode.lstrip()

                if len(city) < 2:
                    city = "<MISSING>"
                if len(street) < 2:
                    street = "<MISSING>"
                if len(state) < 2:
                    state = "<MISSING>"
                if len(pcode) < 2:
                    pcode = "<MISSING>"
                if hours.find('We’re located') > -1:
                    hours = hours[0:hours.find('We’re located')]
                    hours = hours.rstrip()
                if len(hours) < 2:
                    hours =  "<MISSING>"
                phone = phone.lstrip()
                if hours.lower().find('happy') > -1 :
                    hours = hours[0:hours.find('Happy')]
                if hours.lower().find('after') > -1 :
                    hours = hours[0:hours.find('After')]
                hours = hours.rstrip()
                #print(phone)
                #print(hours) 
                data.append([
                    'https://blackfinnameripub.com/',
                    link,                   
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    'US',
                    store,
                    phone,
                    "<MISSING>",
                    "<MISSING>",
                    "<MISSING>",
                    hours
                                ])
                #print(p,data[p])
                p += 1
                #print(".....................")
                
                

                
                
            
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
