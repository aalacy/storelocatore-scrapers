import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('abbeycarpet_com')



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def request_wrapper(url, method, headers, data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = session.get(url, headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    elif method == "post":
        while True:
            try:
                if data:
                    r = session.post(url, headers=headers, data=data)
                else:
                    r = session.post(url, headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    else:
        return None
def fetch_data():
    MAX_RESULTS = 10
    MAX_DISTANCE = 100
    search = sgzip.ClosestNSearch()
    search.initialize()
    zip_code = search.next_zip()
    current_results_len =0
    adress = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.abbeycarpet.com/"
    
    while zip_code:
        result_coords =[]
        #logger.info("zip_code === "+zip_code)
    
        location_url = "https://www.abbeycarpet.com/StoreLocator.aspx?searchZipCode="+str(zip_code)
        try:
            r = request_wrapper(location_url,"get",headers=headers)
            soup = BeautifulSoup(r.text, "lxml")
        except:
            pass
        
        
        data = soup.find_all("div",{"class":"search-store__results-address col-xs-12 col-sm-4"})
        condition = soup.find_all("div",{"class":"search-store__results-links col-xs-12 col-sm-4"})
        current_results_len = len(data)
        hours_of_operation1 = []
        latitude1 =[]
        longitude1 =[]
        for view in condition:
            t = list(view.stripped_strings)
            if len(t) == 3:
                href = "https://abbeycarpet.com"+view.find_all("a")[-1]['href']
                try:
                    r1 = session.get(href,headers=headers)
                except:
                    pass
                soup1 = BeautifulSoup(r1.text, "lxml")
                try:
                    try:
                        hours = soup1.find(text=re.compile(r"\bMon\b")).parent.parent.parent
                    except:
                        hours = soup1.find(text=re.compile(r"\bby appointment only\b")).parent.parent.parent
                except:
                    try:
                        hours = soup1.find(text=re.compile(r"\bMonday\b")).parent.parent.parent
                    except:
                        hours = "<MISSING>"

                
                if soup1.find("div",{"class":"mapWrapper"}) != None:
                    iframe = soup1.find("div",{"class":"mapWrapper"}).find("iframe")
                    src = iframe['src']
                    if hours != None and hours != []:
                        # if type(list(hours.stripped_strings)) != str:
                        try:
                            t = (list(hours.stripped_strings))
                            hours_of_operation = ''.join(t).split('Showroom')[-1].replace('Hours','')
                        except:
                            pass

                    else:
                        latitude = ""
                        longitude = ""
                        hours_of_operation = "<MISSING>" 
                    if src != None and src != []:
                        if "!3d" in src:
                            longitude = src.split('!2d')[1].split('!3d')[0]
                            latitude = src.split('!2d')[1].split('!3d')[1].split('!')[0]                
                        elif "place?zoom" in src:
                            latitude = src.split('=')[2].split(',')[0]
                            longitude = src.split('=')[2].split(',')[1].split('&')[0]   
                        elif "!3f" in src:
                            longitude =  src.split('!2d')[1].split('!3f')[0]
                            latitude = src.split('!2d')[1].split('!3f')[1].split('!4f')[0]
                        else:
                            latitude = ""
                            longitude = ""
                    else:
                        latitude = ""
                        longitude = ""
                
                else:
                    src = soup1.find_all("iframe")[-1]
                    if "!3d" in src["src"]:
                        longitude = src["src"].split('!2d')[1].split('!3d')[0]
                        latitude = src["src"].split('!2d')[1].split('!3d')[1].split('!')[0]                
                    elif "place?zoom" in src:
                        latitude = src["src"].split('=')[2].split(',')[0]
                        longitude = src["src"].split('=')[2].split(',')[1].split('&')[0]   
                    elif "!3f" in src["src"]:
                        longitude =  src["src"].split('!2d')[1].split('!3f')[0]
                        latitude = src["src"].split('!2d')[1].split('!3f')[1].split('!4f')[0]
                    else:
                        latitude = ""
                        longitude = ""
                
            else:
                hours_of_operation = "<MISSING>" 
                latitude = ""
                longitude = ""
            latitude1.append(latitude)
            longitude1.append(longitude)
            hours_of_operation1.append(hours_of_operation)
            
        for index,link in enumerate(data):
            store = []
            t = list(link.stripped_strings)
            if len(t) == 4:
                location_name = t[0]
                street_address = t[1]
                city = t[2].split(',')[0]
                zipp = t[2].split(',')[-1].split(' ')[-1]
                m = t[-2].split(',')[1].strip().split(' ')
                m.pop(-1) 
                state = ' '.join(m)  
                phone = t[3].split('&')[0]
            else:
                location_name = t[1]
                street_address = t[2]
                city = t[3].split(',')[0]
                zipp = t[3].split(',')[-1].split(' ')[-1]
                m = t[-2].split(',')[1].strip().split(' ')
                m.pop(-1) 
                state = ' '.join(m)  
                phone = t[4].split('&')[0]
            
            result_coords.append((latitude1[index] if latitude1 else 0,longitude1[index] if longitude1 else 0))
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state.replace('QC','').replace('N. Carolina','NC'))
            store.append(zipp.replace('H4P2S8',''))   
            store.append("US")
            store.append("<MISSING>")
            store.append(phone.replace('800-709-3550',''))
            store.append("<MISSING>")
            store.append(str(latitude1[index]) if latitude else "<MISSING>")
            store.append(str(longitude1[index]) if longitude else "<MISSING>")
            store.append(hours_of_operation1[index])
            store.append(location_url)     
            if store[2] in adress:
                continue
            adress.append(store[2]) 
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            yield store
             
        if current_results_len < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        
        zip_code = search.next_zip()
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
