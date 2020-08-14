from bs4 import BeautifulSoup
import csv
import string
import re, time, json

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
    p = 0
    cleanr = re.compile(r'<[^>]+>')
    r = session.get('https://www.medmen.com/stores', headers=headers)
    soup = BeautifulSoup(r.text,'html.parser')
    linklist = soup.findAll('a',{'class':'c-stores-list__link'})
    print(len(linklist))
    for link in linklist:
        if link.text.find("Coming Soon") == -1:
            link = 'https://www.medmen.com' + link['href']
            #print(link)
            r = session.get(link, headers=headers)
            soup = BeautifulSoup(r.text,'html.parser')
            title = soup.find('h1').text
            address =str(soup.find('address'))
            address = re.sub(cleanr,'\n',address).lstrip().splitlines()
            street = '<MISSING>'
            #print(address)
            for adr in address:
                if adr == '':
                    pass
                else:
                    if adr.find(', ') > -1:
                        if adr.find(',') > -1 and adr.find('Suit') > -1:
                            street  = adr
                        else:
                            city, state = adr.split(', ',1)
                    else:
                        street  = adr
                        
                        
            
            try:
                state,pcode = state.lstrip().split(' ',1)
            except:
                pcode= "<MISSING>"
            try:
                text = street.split(' ')[0]
            except:
                #print("HER")
                street = '<MISSING>'
                
            phone = soup.findAll('div',{'class':'c-icon-bullet'})[1].text
            hours = soup.findAll('div',{'class':'c-store-details__block'})[1].find('ol').find('li').text
            
            coord ,temp = r.text.split('"'+title + '"'+':{"location":',1)[1].split(',"state"',1)
            coord = json.loads(coord)
            lat = coord["lat"]
            longt = coord['lng']
            store,temp = temp.split(',"locationId":')[1].split(',',1)
            
            if street == '<MISSING>':
                address = temp.split('"address":["',)[1].split('"]')[0].split(',')
                street = address[0]            
                city = address[1]           
                state,pcode = address[2].lstrip().split(' ',1)
            if pcode == '<MISSING>':
                address = temp.split('"address":["',)[1].split('"]')[0].split(',')
                #street = address[0]            
                #city = address[1]           
                pcode = address[2].lstrip().split(' ',1)[1]
            
                
            data.append([
                        ':https://www.medmen.com',
                        link,                   
                        title,
                        street.replace('"',''),
                        city.replace('"',''),
                        state.replace(',','').replace('"',''),
                        pcode.replace('"',''),
                        'US',
                        store,
                        phone,
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
