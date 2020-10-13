from bs4 import BeautifulSoup
import csv
import string
import re, time, usaddress

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
    p = 0
    data = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://portaviarestaurants.com/'
    r = session.get(url, headers=headers, verify=False)   
    soup =BeautifulSoup(r.text, "html.parser")
   
    linklist = soup.findAll('a')
    for link in linklist:
        if link.text.find('Visit Us') > -1:
            link = 'https://portaviarestaurants.com'+link['href']
            print(link)
            r = session.get(link, headers=headers, verify=False)
            soup = BeautifulSoup(r.text,'html.parser')
            title = soup.find('h2',{'class':'elementor-heading-title'}).text
            content = soup.find('ul',{'class': 'elementor-icon-list-items'}).findAll('li')
            phone = content[0].text.strip()
            address = content[2].text.strip()
            hourlist = soup.findAll('div',{'class':'elementor-column-wrap elementor-element-populated'})
            for hr in hourlist:
                if hr.text.find('Hours') > -1:
                    hours = re.sub(cleanr,' ',str(hr))
                    hours = re.sub(pattern,' ',hours).replace('Â','').replace('â','-').lstrip()
                    break
            
            address = usaddress.parse(address)
            i = 0
            street = ""
            city = ""
            state = ""
            pcode = ""
            while i < len(address):
                temp = address[i]
                if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find('Occupancy') != -1 or temp[1].find("Recipient") != -1 or temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find("USPSBoxID") != -1:
                    street = street + " " + temp[0]
                if temp[1].find("PlaceName") != -1:
                    city = city + " " + temp[0]
                if temp[1].find("StateName") != -1:
                    state = state + " " + temp[0]
                if temp[1].find("ZipCode") != -1:
                    pcode = pcode + " " + temp[0]
                i += 1

            street = street.lstrip().replace(',','')
            city = city.lstrip().replace(',','')
            state = state.lstrip().replace(',','')
            pcode = pcode.lstrip().replace(',','')                
   
            data.append([
                        'https://portaviarestaurants.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        '<MISSING>',
                        phone.replace('â\x80\x8b',''),
                        '<MISSING>',
                        '<MISSING>',
                        '<MISSING>',
                        hours
                    ])
            #print(p,data[p])
            p += 1
                
   
    return data


def scrape():   
    data = fetch_data()
    write_output(data)
    

scrape()
