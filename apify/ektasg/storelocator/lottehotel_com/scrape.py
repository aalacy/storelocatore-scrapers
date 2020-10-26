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
    p = 0
    
    url = 'https://www.lottehotel.com/global/en/hotel-finder.html'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")   
    maindiv = soup.findAll('ul', {'class': 'd096-city'})[1].find('ul',{'class':'d096-hotel'})
    
            
    divlist = maindiv.findAll('li')
    for div in divlist:
        link = div.find('p',{'class':'d096-hotel__title'}).find('a')['href']
        if link.find('http') == -1:
            link = 'https://www.lottehotel.com' + link
        title = div.find('p',{'class':'d096-hotel__title'}).find('strong').text.replace('\n','')
        address = div.find('p',{'class':'d096-hotel__address'}).text.replace('\n','')
        phone = div.find('p',{'class':'d096-hotel__tel'}).text.lstrip().split('\n',1)[0]
        address = usaddress.parse(address)
        i = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while i < len(address):
            temp = address[i]
            if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find("USPSBoxID") != -1:
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]

            i += 1
        r = session.get(link, headers=headers, verify=False)  
        soup = str(BeautifulSoup(r.text, "html.parser"))
        start = soup.find('data-latitude=')
        if start == -1:
            start = soup.find("latitude")
            if start == -1:
                lat = '<MISSING>'
                longt = '<MISSING>'
            else:
                lat,longt = soup.split('"latitude":')[1].split(',',1)
                longt = longt.split('"longitude":')[1].split('}',1)[0].replace('"','').lstrip().replace('\n','').rstrip()
                lat = lat.replace('"','').lstrip()
        else:
            lat, longt = soup.split('data-latitude="')[1].split('"',1)
            longt = soup.split('data-longitude="')[1].split('"',1)[0]

        if pcode == '':
            pcode = '<MISSING>'
        try:
            state = state.split(',')[0]
        except:
            pass
        try:
            city = city.split('LOTTE HOTEL')[0]
        except:
            city = '<MISSING>'
            
        data.append([
                        'https://www.lottehotel.com/',
                        link,                   
                        title,
                        street.lstrip(),
                        city.lstrip().replace(',',''),
                        state.lstrip().replace(',',''),
                        pcode.lstrip().replace(',',''),
                        'US',
                        '<MISSING>',
                        phone.replace('+1-',''),
                        '<MISSING>',
                        lat,
                        longt,
                        '<MISSING>'
                    ])
        #print(p,data[p])
        p += 1
        #input("NEXT")
   


           
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
