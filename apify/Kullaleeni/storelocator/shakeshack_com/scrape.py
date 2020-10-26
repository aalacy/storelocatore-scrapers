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
    data = []
    pattern = re.compile(r'\s\s+')
    url = 'https://www.shakeshack.com/locations/'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")    
    p = 0   
    divlist = soup.findAll('div', {'class': 'citys'})[0].findAll('div',{'class':'row-fluid'})
    for div in divlist:
        link = 'https://www.shakeshack.com' + div.find('div',{'class':'title'}).find('a')['href']
        #link = 'https://www.shakeshack.com/location/empire-outlets-staten-island-ny/'
        #print(link)
        
        r = session.get(link, headers=headers, verify=False)  
        soup =BeautifulSoup(r.text, "html.parser")
        title = soup.find('title').text.split(' - ')[0]
        hours = soup.find('div',{'class':'hours-and-transportation'}).find('p').text.replace('Hours:','').replace('\n','')
        det = soup.find('div',{'class':'address'}).text.lstrip().rstrip().split('\n')
        #print(det)
        
        flag = 0
        count = 0
        phone = ''
        address = ''
        #print(dt)
        #input()
        for dt in det :
            temp = dt.replace('.','').replace('-','').replace(')','').replace('(','').replace(' ','').lstrip().rstrip()
            temp = temp.replace('–','')
            temp = temp.replace('Main','')
            if temp.isdigit() and len(temp) == 10:
                #print('1')
                phone = dt
                break
            elif dt.find('Direction') > -1:          
                break
            elif dt.find('Email') > -1 or dt.find('Office') > -1 or dt.find('Just off') > -1:
                pass
            else:
                #print('4')
                count += 1
        #print(temp)
        
        address = ''
        for i in range(0,count):
            address = address + det[i]+ ' '
            
        #
        #print(address)
        check = ''
        try:
            check = address.split('(')[1].split(')')[0]
            check = '('+check+')'            
            address = address.replace(check,'')
            check = check.replace('&\xa0','')
        except:
            pass
        address = usaddress.parse(address)
        #print(address)
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
        lat = str(soup).split('lat:',1)[1].split(',',1)[0]
        longt = str(soup).split('lng:',1)[1].split('}',1)[0]
        street = street.lstrip()
        city = city.lstrip().replace(',','')
        state = state.lstrip().replace(',','')
        pcode = pcode.lstrip().replace(',','')
        
        if len(hours) < 3:
            hours = '<MISSING>'
        if len(phone) < 3:
            phone = '<MISSING>'
        else:
            phone = phone.replace(' – Main','')
        if len(city) < 3 and len(state) < 2:
            try:
                city,state = title.split(',')
            except:
                city,state = title.split(',',1)[1].split(',',1)
                city = city.split(' ')[-1]
        if state.find('NYC') > -1:
            state = 'NY'
            street = street + ' ' + city
            city = 'NYC'
        if len(pcode)  < 3:
            pcode = str(soup).split("geocode({ 'address': '",1)[1].split("'}")[0].split(' ')[-1]
            if len(pcode) == 5 and pcode.isdigit():
                pass
            else:
                pcode = '<MISSING>'
        if hours.find('Check the') > -1 or hours.find('before') > -1:
            hours  = '<MISSING>'
        if city.find('Las Vegas') > -1:
            street = street + ' ' + city.replace('Las Vegas','')
            city = 'Las Vegas'
        if city.find('Lake Grove') > -1:
            street = street + ' ' + city.replace('Lake Grove','')
            city = 'Lake Grove'
        if city.find('New Orleans') > -1:
            street = street + ' ' + city.replace('New Orleans','')
            city = 'New Orleans'

        if check.find('(Queens') > -1:
            city = 'Queens'
            state = 'NY'
        if state.find('DC') > -1 or state.find('D.C') > -1:
            state = 'DC'
            city = 'Washington'
        if state.find('Washington') > -1:
            state = 'WA'
        if len(hours) <3 :
            hours = '<MISSING>'
        if len(phone) < 3:
            phone =  '<MISSING>'
        if len(city) < 3:
            city = '<MISSING>'
        if len(pcode) < 4:
            pcode = '0'+pcode
        if city == '<MISSING>' and street.find('Staten Island') > -1:
            city = 'Staten Island'
            street = street.replace('Staten Island','')
        street = street + ' '+ check
        data.append([
                        'https://www.shakeshack.com',
                        link,                   
                        title,
                        street.replace(',',''),
                        city,
                        state,
                        pcode,
                        'US',
                        '<MISSING>',
                        phone,
                        '<MISSING>',
                        lat,
                        longt,
                        hours.replace('\n',' ').lstrip().rstrip().replace("\xa0",' ')
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
