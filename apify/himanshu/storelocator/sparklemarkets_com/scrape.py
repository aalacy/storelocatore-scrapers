import csv
import requests
from bs4 import BeautifulSoup
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url ='https://www.sparklemarkets.com/'
    bb = 'www.sparklemarkets.com'
    return_main_object = []

    r = requests.get(base_url+'/locations')

    soup = BeautifulSoup(r.text,"lxml")
    # getmain = soup.find('div',{'id':'comp-jqwqcz74inlineContent'}).find_all('a')['href']
    # getmain = soup.find('div',{'class':'style-jqwqcz7u1inlineContent'}).find_all('div',{'role':'row'}).find_all('a',{'class':'g-transparent-a style-jqwqvzxplink'})
    getmain = soup.find_all('a',{'class':'g-transparent-a style-jqwqvzxplink'})
        # .find_all('a',{'class':'g-transparent-a'})

    if getmain != None and getmain != "":

        for i in getmain:
                v = i['href'].split('/')[2]
                if v in bb:
                    getcontent = requests.get(i['href'])
                    soup = BeautifulSoup(getcontent.text,"lxml")
                    for p in soup.find_all("p",{"class":"font_7"}):
                            if p != None:
                                a_data = list(p.stripped_strings)

                                if len(a_data) > 0:

                                    locator_domain = base_url
                                    location_name = soup.find('h1',{'class':'font_2'}).text
                                   
                                    if a_data[0] == 'Address:':

                                        a = a_data[1].replace('\xa0','').strip().split(',')
                                        
                                        if len(a) == 4:
                                            street_address = a[0]+a[1]
                                            city = a[2]
                                            
                                            state = a[3].strip().split(' ')[0]
                                            zip = a[3].strip().split(' ')[1]
                                            
                                        elif len(a) == 3:

                                            street_address = a[0]
                                            city = a[1]
                                            s = a[2].strip()
                                            state = [s[i:i+2] for i in range(0, len(s), 2)][0]
                                            zip = [s[i:i+2] for i in range(0, len(s), 2)][-3]+[s[i:i+2] for i in range(0, len(s), 2)][-2]+[s[i:i+2] for i in range(0, len(s), 2)][-1]
                                           
                                        elif len(a) == 2:
                                            street_address = a[0]
                                            s = a[1].strip()
                                            city = '<MISSING>'
                                            state = [s[i:i+2] for i in range(0, len(s), 2)][0]
                                            zip = [s[i:i+2] for i in range(0, len(s), 2)][-3]+[s[i:i+2] for i in range(0, len(s), 2)][-2]+[s[i:i+2] for i in range(0, len(s), 2)][-1]
                                       
                                        country_code = 'NY'
                                        store_number = '<MISSING>'
                                        phone = a_data[3]
                                        location_type = 'sparklemarkets'
                                        latitude = '<MISSING>'
                                        longitude = '<MISSING>'


                                        if a_data[4] == 'Hours:':
                                            
                                            hours_of_operation = a_data[5]

                                        elif a_data[6] == 'Hours:':
                                            hours_of_operation = a_data[7]

                                        elif a_data[8] == 'Hours:':
                                            hours_of_operation = a_data[9]
                                        
                                        
                                        store = []
                                        store.append(locator_domain if locator_domain else '<MISSING>')
                                        store.append(location_name if location_name else '<MISSING>')
                                        store.append(street_address if street_address else '<MISSING>')
                                        store.append(city if city else '<MISSING>')
                                        store.append(state if state else '<MISSING>')
                                        store.append(zip if zip else '<MISSING>')
                                        store.append(country_code if country_code else '<MISSING>')
                                        store.append(store_number if store_number else '<MISSING>')
                                        store.append(phone if phone else '<MISSING>')
                                        store.append(location_type if location_type else '<MISSING>')
                                        store.append(latitude if latitude else '<MISSING>')
                                        store.append(longitude if longitude else '<MISSING>')                                        
                                        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
                                        return_main_object.append(store)
        return return_main_object

def scrape():
    data = fetch_data()
    # print(data)
    write_output(data)

scrape()
