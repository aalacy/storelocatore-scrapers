from bs4 import BeautifulSoup
import csv
import string
import re
import usaddress
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    p = 0
    url = 'https://locations.rentacenter.com/#contains-place-toggle'
    page= session.get(url, headers=headers, verify=False)
    #page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    mainul = soup.find('div',{'id':'contains-place'})
    statelinks = mainul.findAll('a')
    #print(statelinks)
    cleanr = re.compile(r'<[^>]+>')
    for states in statelinks:
        statelink = 'https://locations.rentacenter.com'+ states['href']+'#contains-place-toggle'
        #print(statelink)
        if True :           
            page1 = session.get(statelink, headers=headers, verify=False)
            soup1 = BeautifulSoup(page1.text, "html.parser")
            mainul1 = soup1.find('div', {'id': 'contains-place'})
            citylinks = mainul1.findAll('a')
            for cities in citylinks:
                citylink = 'https://locations.rentacenter.com'+ cities['href']
                #print(citylink)
                page2 = session.get(citylink, headers=headers, verify=False)
                soup2 = BeautifulSoup(page2.text, "html.parser")
                #mainul2 = soup2.find('ul', {'class': 'list-group'})
                mainul2 = soup2.find('div', {'id': 'nearby-locations'})
                branchlinks = mainul2.findAll('div',{'class':'location-nearby'})
                #print(len(branchlinks))              
                if len(branchlinks) > 0:
                    for branch in branchlinks:
                        link = 'https://locations.rentacenter.com'+ branch.find('a',{'class':'location-nearby-name'})['href']
                        #print(link)
                        phone = '<MISSING>'
                        lat =  '<MISSING>'
                        longt =  '<MISSING>'
                        hours =  '<MISSING>'

                        lat,longt = branch.find('a',{'class':'location-nearby-directions'})['href'].split('/')[-1].split(',')
                        address = branch.find('div',{'class':'location-nearby-address'})
                        address = re.sub(cleanr,' ',str(address)).replace('\n','')
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
                        try:
                            phone = branch.find('a',{'class':'location-nearby-phone-number'}).text
                        except:
                            '<MISSING>'
                        try:
                            hours = branch.find('div', {'class': 'location-nearby-hours'}).find('dl').text
                            hours = hours.replace("\n", " ")
                            hours = hours.strip()
                        except:
                            hours = "<MISSING>"
                        street = street.lstrip()
                        state = state.lstrip()
                        city = city.lstrip().replace(',','')
                        pcode = pcode.lstrip()
                        title = 'Rent-A-Center at '+street +', '+state+', '+pcode
                        if len(phone) < 3:
                            phone = '<MISSING>'
                        if len(hours) < 3:
                            hours = '<MISSING>'
                        if len (lat) < 3 or lat == 'false':
                            lat = '<MISSING>'
                        if len(longt) <3 or longt == 'false':
                            longt = '<MISSING>'
                        if len(street) <3:
                            street = '<MISSING>'
                        if len(city) < 3:
                            city = '<MISSING>'
                        if len(pcode) <3:
                            pcode =  '<MISSING>'
                        
                        data.append(['https://www.rentacenter.com/', link, title, street, city, state, pcode,'US', '<MISSING>', phone.lstrip(), '<MISSING>', lat ,longt, hours])
                        #print(p,data[p])
                        #input()
                        p += 1

                else:                   
                    pass
            
            
    return data



def scrape():

    data = fetch_data()
    write_output(data)


scrape()

