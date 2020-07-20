import requests
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
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://cookiecorner.com/about/store_locations'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")
    maindiv = str(soup.find('div',{'id':'main'}))
    maindiv = maindiv[maindiv.find('<h3>'):maindiv.find('<br></div>',maindiv.find('<h3>'))]
    maindiv = re.sub(cleanr,'\n',str(maindiv)).splitlines()
    m = 0
    flag = 0
    title = ''
    address = ''
    phone = ''
    hours = ''
    while m < len(maindiv):
        #print(maindiv[i])
        
        if maindiv[m] == '':
            pass
        else:
            if maindiv[p].islower() == False and (flag == 0 or flag == 4) and maindiv[m].find('Sunday') == -1:
                #print(maindiv[m])
                if flag == 4:
                    #print(p,"Result=",title,address,phone,hours)
                    address = usaddress.parse(address)
                    i = 0
                    street = ""
                    city = ""
                    state = ""
                    pcode = ""
                    while i < len(address):
                        temp = address[i]
                        if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find(
                            "USPSBoxID") != -1:
                            street = street + " " + temp[0]
                        if temp[1].find("PlaceName") != -1:
                            city = city + " " + temp[0]
                        if temp[1].find("StateName") != -1:
                            state = state + " " + temp[0]
                        if temp[1].find("ZipCode") != -1:
                            pcode = pcode + " " + temp[0]
                        i += 1
                    if len(pcode) < 3:
                        pcode = '<MISSING>'
                        
                    data.append([
                        'https://cookiecorner.com/',
                        'https://cookiecorner.com/about/store_locations',                   
                        title,
                        street.lstrip().replace(',',''),
                        city.lstrip().replace(',',''),
                        state.lstrip(),
                        pcode.lstrip(),
                        'US',
                        '<MISSING>',
                        phone,
                        '<MISSING>',
                        '<MISSING>',
                        '<MISSING>',
                        hours.rstrip()
                    ])
                    #print(p,data[p])
                    p += 1
                    title = ''
                    address = ''
                    phone = ''
                    hours = ''
                   
                
                flag = 1
                title = maindiv[m]
                #input(flag)
                    
            elif phone == '' and maindiv[m].find('-') > -1 and flag == 1:
                phone = maindiv[m]
                flag = 2
            elif address == '' and flag == 2:
                address = maindiv[m]
                flag = 3
            elif (flag == 3 or flag == 4) and (maindiv[m].find('p.m.')> -1 or maindiv[m].find('COVID-19') > -1) :               
                hours =    hours + maindiv[m]+ ' '
                flag = 4
            else:
                pass
            
     
        m += 1
     
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
