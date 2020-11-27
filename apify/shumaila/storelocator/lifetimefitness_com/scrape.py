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
    # Your scraper here
    
    data = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://www.lifetime.life/view-all-locations.html'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")
    linklist = soup.select("a[href*=time-locations]")
   # print("states = ",len(state_list))
    p = 0
    for link in linklist:
        if 'http' in link['href']:
            link = link['href']
            
        else:
            link = 'https://www.lifetime.life'+ link['href']
        #print(link)
        if 'life-time-locations.html' in link:
            continue
        r = session.get(link, headers=headers, verify=False)  
        soup =BeautifulSoup(r.text, "html.parser")
        title = soup.find('h1').text
        try:
            address = soup.find('div',{'class':'hero-content'}).select_one("a[href*=maps]")        
            lat,longt = address['href'].split('@',1)[1].split('data',1)[0].split(',',1)
        except:
            continue
        longt = longt.split(',',1)[0]
        address = usaddress.parse(address.text)
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
        ccode = 'US'
        phone = soup.find('div',{'class':'hero-content'}).select_one("a[href*=tel]").text
        try:
            hourslink = soup.find('div',{'class':'hero-content'}).select_one('a:contains("Club Hours")')
            if hourslink.text.find('Future') > -1:
                continue
            hourslink = 'https://www.lifetime.life'+ hourslink['href']
        except:
            continue
        r = session.get(hourslink, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            hours = soup.find('table').text
            hours = re.sub(pattern,'\n',hours).replace('\n',' ').replace('Hours','').replace('Day','').replace('HOURS','').strip()
        except:
            hours = '<MISSING>'
        if len(pcode) < 4:
            state,temp = state.split(' ',1)
            pcode = temp +' '+ pcode
            ccode = "CA"
        data.append([
                        'https://www.lifetime.life/',
                        link,                   
                        title,
                        street.strip(),
                        city.strip(),
                        state.strip(),
                        pcode.strip(),
                        ccode,
                        '<MISSING>',
                        phone.replace('\n',''),
                        '<MISSING>',
                        lat,
                        longt,
                        hours
                    ])
        #print(p,data[p])
        p += 1
                
            
      
        
    return data


def scrape():
  
    data = fetch_data()
    write_output(data)
 
scrape()
