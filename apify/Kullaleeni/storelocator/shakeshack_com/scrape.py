from bs4 import BeautifulSoup
import csv
import string,usaddress
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
    url = 'https://www.shakeshack.com/locations/'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")   
    divlist = soup.findAll('div', {'class': 'citys'})[0].findAll('div',{'class':'address_div'})
    coordlist = str(soup).split('window.locations = [',1)[1].split('}]',1)[0]
    coordlist ='[' + coordlist + '}]'
    #print(coordlist)
    p = 0
    coordlist = json.loads(coordlist)
    for div in divlist:
        
        #input()
        title = div.find('div',{'class':'title'}).text.replace('\n','')
        link = 'https://www.shakeshack.com' + div.find('div',{'class':'title'}).find('a')['href']
        #print(title)
        address = ''
        lat = '<MISSING>'
        longt = '<MISSING>'
        for coord in coordlist:
            try:
                if title == coord['name']:
                    lat = coord['lat']
                    longt = coord['long']
                    address = coord['directionsLink'].replace('\r\n',' ')            
                    break
            except:
                address = ''
                break
                

        if address == '':
            continue
        
       
        address = div.find('div',{'class':'address'}).text.lstrip().splitlines()        
        
       
        i = 0
        state = ''
        pcode = ''
        street = ''
        city = ''
        phone = ''
        temp = 0
        for i in range(0,len(address)):           
            adr = address[i]          
            if (adr.find('.') > -1 and adr.split('.')[0].isdigit()) or (adr.find('-') > -1 and adr.find('(') > -1) or adr.find('-') > -1 and len(adr.split('-')[0]) ==3 and adr.split('-')[-1] == 4:
                check = adr.replace('-','').replace('(','').replace(')','').replace('.','')
                if check.isdigit():
                    phone = adr
                    temp = i
                    break
                else:
                    pass
                
        if phone == '':
            temp = len(address)
            
        address = ' '.join(address[0:temp])
        try:
            address= address.split('Email')[0]
        except:
            pass
        check = ''
        try:
            check = address.split('(')[1].split(')')[0]
            address = address.split('(')[0]+' '+address.split(')')[1]
        except:
            pass
            
        print(address)
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
            
        state = state.lstrip().replace(',','')
        pcode = pcode.lstrip().replace(',','')
        street = street.lstrip().replace(',','')
        city = city.lstrip().replace(',','')
        street = street + ' ' + check
        hours = div.find('div',{'class':'opening'}).text.lstrip()
        if len(phone) < 3:
            phone = '<MISSING>'
        if len(hours) < 3:
            hours = '<MISSING>'
        if state == '' and city == '':
            temp= title.split(', ')
            print(temp)
            state = temp[-1]
            city = temp[-2]
        if state == '' :
            temp= title.split(', ')
            #print(temp)
            state = temp[-1]
            if city != temp:
                street = street + ' '+city
                city = temp[-2]
        if len(pcode) < 3:
            pcode = '<MISSING>'
        if len(state) < 2:
            state = '<MISSING>'
        if len(street) < 3:
            street = '<MISSING>'

        if len(city) < 3:
            city = '<MISSING>'
        if state == 'NYC':
            state = 'NY'
        data.append([
                        'https://www.shakeshack.com',
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
                        hours.replace('\n',' ').lstrip().rstrip()
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
