from bs4 import BeautifulSoup
import csv
import string
import re, time

from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'token':'SFNZAIIBLMQAAYVQ'
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
    data = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://www.craftrepublic.com/locations/'
    r = session.get(url, headers=headers, verify=False)   
    soup =BeautifulSoup(r.text, "html.parser")   
    linklist = soup.findAll('a', {'class': "locationLink"}) 
    p = 0
    for link in linklist:
       if True:
            title = link.text
            link = 'https://www.craftrepublic.com' + link['href']
            #print(link)
            r = session.get(link, headers=headers, verify=False)
            soup =BeautifulSoup(r.text, "html.parser")
            title = soup.find('title').text.split(':')[0]
            address = re.sub(cleanr,' ',str(soup.find('div',{'class':'locations-address'})))
            address = address.strip().splitlines()
            street = address[0]
            city, state =address[1].split(', ')
            state,pcode = state.lstrip().split(' ',1)
            phone = soup.find('a',{'class':'locations-address'}).text
            lat,longt = soup.find('a',{'class':'locationButton'})['href'].split('Location/',1)[1].split(',')
            lat = lat.replace('+','')
            store = str(soup).split('location_id="',1)[1].split('">')[0]
            hourlink = 'https://partner-api.momentfeed.com/locations/cards?location_id='+store+'&card_id=7'
            r = session.get(hourlink, headers=headers, verify=False)
            hours = BeautifulSoup(r.text, "html.parser").find('div').text
            hours = re.sub(pattern,'',hours).split('Monday',1)[1].replace('\n',' ')
            hours = 'Monday ' + hours 
            data.append([
                        'https://www.craftrepublic.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        store,
                        phone.replace('\n','').strip(),
                        '<MISSING>',
                        lat,
                        longt,
                        hours
                    ])
            #print(p,data[p])
            p += 1
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
