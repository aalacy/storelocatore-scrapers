import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip




def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:

            writer.writerow(row)


def fetch_data():
    base_url ="http://suzuki.com"
    return_main_object=[]
    output=[]
    zips=sgzip.for_radius(100)
    for zp in zips:
        try:
            r = requests.get(base_url+'/DealerSearchHandler.ashx?zip='+zp+'&hasCycles=false&hasAtvs=false&hasScooters=false&hasMarine=false&hasAuto=true&maxResults=4&country=en')
            soup=BeautifulSoup(r.text,'lxml')
        except:
            continue
        for loc in soup.find_all('dealerinfo'):
            name=loc.find('name').text.strip()
            address=loc.find('address').text.strip().lower()
            city=loc.find('city').text.strip()
            state=loc.find('state').text.strip()
            zip=loc.find('zip').text.strip()
            phone=loc.find('phone').text.strip()
            country=loc.find('country').text.strip()
            storeno=loc.find('dealerid').text.strip()
            lat=loc.find('esriy').text.strip()
            lng=loc.find('esrix').text.strip()
            hour = loc.find('hoursdetails').text
            kk = []
            if len(hour.split('|')) > 1:

                for id,x in enumerate(hour.split('|')):
                    if id != 0:
                        if x != '':
                            a = int(int(x) - 1)

                            b  = int(int(a)/2)


                            if (id % 2) == 0:

                                if b  == 13:
                                    kk.append("1 close ")
                                elif b == 14:
                                    kk.append("2 close ")
                                elif b == 15:
                                    kk.append("3 close ")
                                elif b == 16:
                                    kk.append("4 close ")
                                elif b == 17:
                                    kk.append("5 close ")
                                elif b == 18:
                                    kk.append("6 close ")
                                elif b == 19:
                                    kk.append("7 close ")
                                elif b == 20:
                                    kk.append("8 close ")
                                elif b == 21:
                                    kk.append("9 close ")
                                elif b == 22:
                                    kk.append("10 close ")
                                elif b == 23:
                                    kk.append("11 close ")
                                elif b == 24:
                                    kk.append("12 close ")
                                elif type(b) == 'float':
                                    kk.append(str(b.replace("5","3"))," close ")
                                else:

                                    kk.append(str(b) + " close ")
                            else:

                                if b == 13:
                                    kk.append("1 open ")
                                elif b == 14:
                                    kk.append("2 open ")
                                elif b == 15:
                                    kk.append("3 open ")
                                elif b == 16:
                                    kk.append("4 open ")
                                elif b == 17:
                                    kk.append("5 open ")
                                elif b == 18:
                                    kk.append("6 open ")
                                elif b == 19:
                                    kk.append("7 open ")
                                elif b == 20:
                                    kk.append("8 open ")
                                elif b == 21:
                                    kk.append("9 open ")
                                elif b == 22:
                                    kk.append("10 open ")
                                elif b == 23:
                                    kk.append("11 open ")
                                elif b == 24:
                                    kk.append("12 open ")
                                elif type(b) == 'float':
                                    kk.append(str(b.replace("5", "3")), " open ")
                                else:
                                    kk.append(str(b) + " open ")
                        else:
                            kk.append('close')
            if kk != []:

                hour = ' , '.join(kk)

            store=[]
            store.append(base_url)
            store.append(name if name else "<MISSING>")
            store.append(address if address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zip if zip else "<MISSING>")
            store.append(country if country else "<MISSING>")
            store.append(storeno if storeno else "<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(lat if lat else "<MISSING>")
            store.append(lng if lng else "<MISSING>")
            store.append(hour if hour.strip() else "<INACCESSIBLE>")
            store.append(base_url+'/DealerSearchHandler.ashx?zip='+zp+'&hasCycles=false&hasAtvs=false&hasScooters=false&hasMarine=false&hasAuto=true&maxResults=4&country=en')
            
            ads = address + ' ' + city + ' ' + state + ' ' + zip
            if ads not in output:
                output.append(ads)
                yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
