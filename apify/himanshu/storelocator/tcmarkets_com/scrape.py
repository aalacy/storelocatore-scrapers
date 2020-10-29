import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('tcmarkets_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://tcmarkets.com"
    r = session.get(base_url+'/store-finder/')
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find_all('a',{'itemprop':"url"})
    del main[0]
    for li in main:
        r1 = session.get(li['href'])
        soup1=BeautifulSoup(r1.text,'lxml')

        # exit()
        if soup1.find('div',{'class':"fl-node-5724cee2beac3"})!=None:
            main1=soup1.find('div',{'class':"fl-node-5724cee2beac3"}).find_all('p')
            name=list(soup1.find('div',{"class":"fl-node-5724e69d76150"}).stripped_strings)[0].strip()
            phone=''
            zip=''
            city=''
            state=''
            for ptag in main1:
                if "Store Address" in ptag.text and "Store Hours" in ptag.text:
                    madd=list(ptag.stripped_strings)
                    address=madd[1].strip()
                    ct=madd[2].strip().split(',')
                    city=ct[0].strip()
                    state=ct[1].strip().split(' ')[0].strip()
                    zip=ct[1].strip().split(' ')[1].strip()
                    phone=madd[3].strip()
                    del madd[0]
                    del madd[0]
                    del madd[0]
                    del madd[0]
                    hour=' '.join(madd)
                else:
                    if "Store Address" in ptag.text:
                        madd=list(ptag.stripped_strings)
                        address=madd[1].strip()
                        ct=madd[2].strip().split(',')
                        city=ct[0].strip()
                        if len(madd)==3:
                            ct=madd[1].split(',')
                            if len(ct)>1:
                                phone=madd[-1]
                                ctm=ct[0].strip().split(' ')
                                city=ctm[-1].strip()
                                address=' '.join(ctm)
                                st=ct[1].strip().split(' ')
                                if len(st)==1:
                                    if re.search(r'\d', st[0]):
                                        zip=st[0].strip()
                                    else:
                                        state=st[0].strip()
                                else:
                                    state=st[0].strip()
                                    zip=st[1].strip()
                            else:
                                ct=madd[2].strip().split(',')
                                city=ct[0].strip()
                                st=ct[1].strip().split(' ')
                                state=st[0].strip()
                                zip=st[1].strip()
                        if len(madd)>3:
                            st=ct[1].strip().split(' ')
                            if len(st)==1:
                                if re.search(r'\d', st[0]):
                                    zip=st[0].strip()
                                    ctm=ct[0].strip().split(' ')
                                    if len(ctm)>1:
                                        city=ctm[0]
                                        state=ctm[1]
                                else:
                                    state=st[0].strip()
                            else:
                                state=st[0].strip()
                                zip=st[1].strip()
                            phone=madd[3].strip()
                    if "Store Hours" in ptag.text:
                        madd=list(ptag.stripped_strings)
                        hour=' '.join(madd)
                if "Fuel Station" in ptag.text:
                    madd=list(ptag.stripped_strings)
                    hour+=" "+' '.join(madd)
            country="US"
            lat=''
            lng=''
            # logger.info(name)
            # logger.info(soup1.find('p', {'style': 'text-align: center;'}).text)
            phone = soup1.find('p', {'style': 'text-align: center;'}).text.replace('Phone: ', '').split('~')[0].replace('Phone:', '').strip().strip()
            if '&' in phone:
                phone  = phone.split('&')[0].strip()
                
            page_url = base_url+'/store-finder/'
            # logger.info('~~~~~~~~~~~~~~~~~~')
            store=[]
            store.append(base_url)
            store.append(name if name else "<MISSING>")
            store.append(address if address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zip if zip else "<MISSING>")
            store.append(country if country else "<MISSING>")
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(lat if lat else "<MISSING>")
            store.append(lng if lng else "<MISSING>")
            store.append(hour if hour else "<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
