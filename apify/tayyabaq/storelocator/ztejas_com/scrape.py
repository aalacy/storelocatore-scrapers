import csv
import re
import requests
from bs4 import BeautifulSoup
import usaddress


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)
 
def fetch_data():
    data = []
    p = 0

    url ="https://ztejas.com/locations/"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    mainlist = soup.find('aside').findAll('a')
    for repo in mainlist:        
        link = 'https://ztejas.com/locations/' + repo['href']+'/contact/'
        title = repo.text
        #print(link)
        page1 = requests.get(link)        
        #driver.get(link)
        #time.sleep(5)
        soup1 = BeautifulSoup(page1.text, 'html.parser')
        coord = soup1.find('div',{'class':'marker'})
        lat = coord['data-lat']
        longt = coord['data-lng']
        contact = soup1.find('div',{'class':'contact-info'}).text
        #print(contact)
        start = contact.find('Phone')
        address = contact[0:start]
        end = contact.find('Fax')
        phone = contact[start:end]
        phone = phone.replace('Phone:','')
        phone = phone.replace('\n','')
        address = address.replace('\n',' ')
        address = address.replace('Contact','')
        address = usaddress.parse(address)        
        m = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while m < len(address):
            temp = address[m]                
            if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find(
                    "USPSBoxID") != -1:
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]                    
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
                
            m += 1

        street = street.lstrip()
        city = city.lstrip()
        state = state.lstrip()
        pcode = pcode.lstrip()
        
        start = contact.find('Dining Hours')
        end = contact.find('Happy Hours')
        hours = contact[start:end]
         
        if len(hours) < 1:
            contact = str(soup1)
            start = contact.find('Dining Hours')
            end = contact.find('Happy Hours')
            hours = contact[start:end]
            cleanr = re.compile('<.*?>')
            hours = re.sub(cleanr, '', hours)
            #print(hours)
        hours = hours.replace('\n', ' ')
        hours = hours.replace('Hours', 'Hours ')        
        hours = hours.replace('Dining Hours','')
        phone = phone.lstrip()
        city = city.replace(',','')
        if street.find('(') > -1 and street.find("Z’Tejas") > -1:
            temp = street
            street = street[0:street.find('(')]
            phone = temp[temp.find('('):temp.find('Z')]
            
        street = street.rstrip()
        phone = phone.rstrip()
        
        data.append([
             'https://ztejas.com/',
              link,
              title,
              street,
              city,
              state,
              pcode,             
              'US',
              '<MISSING>',
              phone,
              '<MISSING>',
              lat,
              longt,
              hours
            ])
        #print(data[p])
        #p += 1
        
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
