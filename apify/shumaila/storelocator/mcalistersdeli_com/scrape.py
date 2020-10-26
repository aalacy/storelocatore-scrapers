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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    
    url = 'https://www.mcalistersdeli.com/locations'
    r = session.get(url, headers=headers, verify=False)
  
    soup =BeautifulSoup(r.text, "html.parser")
   
    state_list = soup.find('ul', {'class': 'cpt-state-city-list'}).findAll('a')
    print("states = ",len(state_list))
    
    p = 0
    for states in state_list:
        print(states.text)
        states = 'https://www.mcalistersdeli.com' + states['href']
        r = session.get(states, headers=headers, verify=False)
        ccode = 'US'
        soup = BeautifulSoup(r.text, "html.parser")
        city_list = soup.find('ul', {'class': 'cpt-state-city-list'}).findAll('a')

        #print("cities = ",len(city_list))
        

        for cities in city_list:
            #cities = cities.find('a')
            #print(cities.text.strip())
            cities = 'https://www.mcalistersdeli.com' + cities['href']
            r = session.get(cities, headers=headers, verify=False)
            
            soup = BeautifulSoup(r.text, "html.parser")
            branch_list = soup.find('div', {'class': 'sct-locations-list'}).findAll('p',{'class':'itm-store-name'})
            #print("Branches",len(branch_list),cities)

            for branch in branch_list:
                link = 'https://www.mcalistersdeli.com' + branch.find('a')['href'] 
                        
                r = session.get(link, headers=headers, verify=False)
                soup = BeautifulSoup(r.text, "html.parser")
                title = soup.find('h1',{'class':'itm-location-name'}).text.replace('\n','').replace('\r','').split(':')[0]
                address = soup.find('p',{'class':'itm-location-address'}).find('a')['aria-label']
                temp = address.split(', ')
                state,pcode = temp[-1].split(' ',1)
                city = temp[-2]
                count = len(temp)- 2
                street = '' 
                for i in range(0,count):
                    street = street + ' ' + temp[0]
                try:
                    phone =  soup.find('p',{'class':'itm-location-phone'}).text
                except:
                    phone = '<MISSING>'
                try:
                    hours= ''
                    hourlist = soup.find('dl',{'class':'cpt-location-hours'})
                    days = hourlist.findAll('dt')
                    times = hourlist.findAll('dd')
                    for i in range(0,len(days)):
                        hours = hours + days[i].text + " : " + times[i].text + ' ' 
                        
                except:
                    hours = '<MISSING>' 
                    
                try:
                    coord = soup.find('div',{'class':'itm-location-map'}).find('img')['src'].split('(',1)[1].split(')',1)[0]
                    longt,lat = coord.split(',')
                except:
                    lat =  '<MISSING>'
                    longt =  '<MISSING>'

                try:
                    store = link.split('-')[-1]
                except:
                    store =  '<MISSING>'
                try:
                    pcode = pcode.split('-')[0]
                except:
                    pcode =  '<MISSING>'

                    
                data.append([
                        'https://www.mcalistersdeli.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
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
                #input()
                

                
                
            
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
