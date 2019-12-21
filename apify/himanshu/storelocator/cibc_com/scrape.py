import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time
import sgzip
import pprint


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    return_main_object = []
    base_url = "https://www.cibc.com"
    addressess = []
    search = sgzip.ClosestNSearch()
    search.initialize(include_canadian_fsas = True)
    # print("====")

    MAX_RESULTS = 51
    MAX_DISTANCE = 50
    current_results_len = 0 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',

    }
    coord = search.next_zip()
    while coord:
        count = 0
        result_coords =[]
        locator_domain = "https://www.cibc.com"
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "CA"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""
        page_url = ''
        # print("==============",str(search.current_zip))
        # "N4W"
        # data1 = "useCookies=1&lang=&q=A1A+1A1&searchBranch=1&searchATM=1"search.current_zip
        count = 1
        while True:
            try:
                r = requests.get("https://locations.cibc.com/search/nl/st+john%e2%80%99s?t=&q="+str(search.current_zip)+"&page="+str(count),headers=headers)
            except:
                pass
            soup=BeautifulSoup(r.text,'lxml')
            name = soup.find_all("span",{"itemprop":"location"})
            phone1 = soup.find_all("span",{"itemprop":"telephone"})
            st  = soup.find_all("span",{"itemprop":"streetAddress"})
            city1  = soup.find_all("span",{"itemprop":"addressLocality"})
            zip1  = soup.find_all("span",{"itemprop":"postalCode"})
            state1  = soup.find_all("span",{"itemprop":"addressRegion"})
            hours1  = soup.find_all("div",{"class":"locationHours bankHours"})
            a_tage  = soup.find_all("a",{"class":"resultname"})
            type1 = soup.find_all("div",{"class":"locationType"})
            
            if st!= None and st !=[]:
                current_results_len =len(st)
                for i in range(len(name)):
                    location_name = name[i].text.strip()
                    title = a_tage[i].attrs['title']
                    # print(a_tage[i]['href'])
                    r1 = requests.get("https://locations.cibc.com"+a_tage[i]['href'], headers=headers)
                    soup1=BeautifulSoup(r1.text,'lxml')
                    hours_of_operation = soup1.find("div",{"class":"locationHours bankHours"})
                    hours_of_operation2 = soup1.find("div",{"class":"locationHours tellerHours"})
                    page_url = "https://locations.cibc.com"+a_tage[i]['href']
                    try:
                        latitude = soup1.find("meta",{"itemprop":"latitude"}).attrs['content']
                    except:
                        latitude =''
                    
                    try:
                        longitude = soup1.find("meta",{"itemprop":"longitude"}).attrs['content']
                    except:
                        longitude =''

                    hours_of_operation1 = ''
                    hours_of_operation3 = ''
                    try:
                        hours_of_operation1 = " ".join(list(hours_of_operation.stripped_strings)).replace("Banking Centre Hours Banking Centre Hours","Banking Centre Hours ")
                    except:
                        hours_of_operation1 =''
                    
                    try:
                        hours_of_operation3 = " ".join(list(hours_of_operation2.stripped_strings)).replace("Teller Service Hours Teller Service Hours"," Teller Service Hours")
                    except:
                        hours_of_operation3 =''

                    # print(hours_of_operation1+ ' '+hours_of_operation3)
                    all_hours = hours_of_operation1 + ' '+hours_of_operation3
                    # print(all_hours)
                    try:
                        phone = phone1[i].text.strip()
                    except:
                        phone = "<MISSING>"

                    street_address  = st[i].text.strip()

                    try:
                        city =  city1[i].text.strip()
                    except:
                        city = "<MISSING>"
                    try:
                        state = state1[i].text.strip()
                    except:
                        state = "<MISSING>"
                    try:
                        zipp = zip1[i].text.strip()
                    except:
                        zipp = "<MISSING>"
                  
                    try:
                        # location_type = type1[i].text.strip()
                        location_type  = re.sub(r"\s+", " ", type1[i].text).replace("\n","")
                        
                    except:
                        location_type=''
    
                    # print("=============-------------------------",location_type)
                    store = []
                    result_coords.append((latitude, longitude))
                    store.append(locator_domain if locator_domain else '<MISSING>')
                    store.append(location_name.encode('ascii', 'ignore').decode('ascii').strip() if location_name else '<MISSING>')
                    store.append(street_address.encode('ascii', 'ignore').decode('ascii').strip() if street_address else '<MISSING>')
                    store.append(city.strip().encode('ascii', 'ignore').decode('ascii').strip() if city else '<MISSING>')
                    store.append(state.strip().encode('ascii', 'ignore').decode('ascii').strip() if state else '<MISSING>')
                    store.append(zipp if zipp else '<MISSING>')
                    store.append(country_code if country_code else '<MISSING>')
                    store.append(store_number if store_number else '<MISSING>')
                    store.append(phone.encode('ascii', 'ignore').decode('ascii').strip() if phone else '<MISSING>')
                    store.append(location_type if location_type else '<MISSING>')
                    store.append(latitude if latitude else '<MISSING>')
                    store.append(longitude if longitude else '<MISSING>')
                    store.append(all_hours.strip().lstrip().replace('Banking Centre Hours','').encode('ascii', 'ignore').decode('ascii').strip() if all_hours.strip().lstrip().replace('Banking Centre Hours','') else '<MISSING>')
                    store.append(page_url if page_url else '<MISSING>')
                    if store[2] in addressess:
                        continue
                    addressess.append(store[2])
                    # print("====================",store)
                    yield store
            else:
                break
            count +=1
                
                  
        # print("==================================",current_results_len)
        if current_results_len < MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_zip()



def scrape():
    data  = fetch_data()
    write_output(data)

scrape()
