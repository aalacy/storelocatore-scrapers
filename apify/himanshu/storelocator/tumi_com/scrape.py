import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('tumi_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def minute_to_hours(time):
    am = "AM"
    hour = int(time / 60)
    if hour > 12:
        am = "PM"
        hour = hour - 12
    if int(str(time / 60).split(".")[1]) == 0:
        
        return str(hour) + ":00" + " " + am
        
    else:
        k1 = str(int(str(time / 60).split(".")[1]) * 6)[:2]
        # logger.info(k1[:2])
        # round(answer, 2)
        return str(hour) + ":" + k1 + " " + am
        


def fetch_data():
    return_main_object = []
    store_detail=[]
    store_name=[]

    addressess = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 100
    current_results_len = 0  # need to update with no of count.
    zip_code = search.next_zip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',

    }

    while zip_code:
        j =0
        result_coords = []
        while j!=-1:
            r = session.get("https://www.tumi.com/store-finder?q="+str(zip_code)+"&searchRadius="+str(MAX_DISTANCE)+"&page="+str(j),
                headers=headers)
            soup1= BeautifulSoup(r.text,"lxml")
            id1 = soup1.find("form",{"id":"myStoreForm"})
            soup2 =soup1.find_all("div",{"class":"span12"})
            current_results_len = len(soup2)
            if id1 == None:
                j=-1
            else:
                j=j+1
                for i in soup2:
                    k = i.find("div",{"class":"locator-storedetails"})
                    if k != None:
                        tem_var=[]
                        link_store = (k.find("div",{"class":"locator-storename"}).a['href'])
                        lng = k.find("div",{"class":"locator-storename"}).a['href'].split('lat=')[1].split("&long=")[1].split("&")[0]
                        lat =k.find("div",{"class":"locator-storename"}).a['href'].split('lat=')[1].split("&long=")[0]
                        name = k.find("div",{"class":"locator-storename"}).a.text.replace("\t","").replace("\n","").replace(u"\xa0-\xa0",u"")
                        st1 = list(k.find("div",{"class":"locator-address"}))
                        if len(st1)==10:
                            st = st1[0].replace('\t',"").replace("\n"," ")
                            state = st1[4].strip().split('-')[0]
                            phone = st1[7].text
                            city2=st1[2].replace('\t',"").replace("\n","").split(",")
                            if len(city2)==2:
                                city = city2[0].rstrip()
                                state = city2[1]
                            else:
                                city = city2[0].rstrip()
                                state = "<MISSING>"
                            zip1 = (st1[4].strip().split('-')[0])
                        else:
                            phone  = st1[-3].text
                            del st1[1]
                            st = " ".join(st1[:2])
                            city = st1[3].replace('\t',"").replace("\n","").strip().split(',')[0]
                            state1= st1[3].replace('\t',"").replace("\n","").strip().split(',')
                            if len(state1)==1:
                                state1 =  "<MISSING>"
                            else:
                                if state1[-1]:
                                    state = state1[-1]
                                else:
                                    state = "<MISSING>"
                            zip1 = st1[5].strip().split('-')[0].strip().replace("\n","")
                            phone  = st1[8].text
                        time = k.find("ul",{"class":"locator-hours"})
                        if time != None:
                            time1 = " ".join(list(time.stripped_strings))
                        else:
                            time1 = "<MISSING>"
                        

                        if len(zip1.strip())==6 or len(zip1.strip())==7:
                            contry = "CA"
                        else:
                            contry = "US"
                        
                        # logger.info("===lennnnnnnnnnn=======",len(zip1.strip()))

                        
                        # logger.info("===zippppppppppppppppppppp=======",zip1)    
                        latitude = lat
                        longitude = lng
                        tem_var.append("https://www.tumi.com")
                        result_coords.append((latitude, longitude))
                        tem_var.append(name.encode('ascii', 'ignore').decode('ascii').strip() if name  else "<MISSING>")
                        tem_var.append(st.replace('\t',"").replace("\n","").encode('ascii', 'ignore').decode('ascii').strip() if st else "<MISSING>")
                        tem_var.append(city.lstrip().rstrip().encode('ascii', 'ignore').decode('ascii').strip() if city else "<MISSING>")
                        tem_var.append(state.encode('ascii', 'ignore').decode('ascii').strip() if state else "<MISSING>" )
                        tem_var.append(zip1.encode('ascii', 'ignore').decode('ascii').strip() if zip1 else "<MISSING>")
                        tem_var.append(contry)
                        tem_var.append("<MISSING>")
                        tem_var.append(phone.encode('ascii', 'ignore').decode('ascii').strip() if phone else "<MISSING>" )
                        tem_var.append("<MISSING>")
                        tem_var.append(lat.encode('ascii', 'ignore').decode('ascii').strip() if lat else "<MISSING>" )
                        tem_var.append(lng.encode('ascii', 'ignore').decode('ascii').strip() if lng else  "<MISSING>")
                        tem_var.append(time1.encode('ascii', 'ignore').decode('ascii').strip() if time1 else "<MISSING>")
                        tem_var.append("https://www.tumi.com"+link_store)
                        if tem_var[2] in addressess:
                            continue
                        addressess.append(tem_var[2])
                        # logger.info("=============================",tem_var)
                        yield tem_var
                        
        if current_results_len < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
    # for i in range(len(store_name)):
    #    store = list()
    #    store.append("https://www.tumi.com")
    #    store.append(store_name[i])
    #    store.extend(store_detail[i])
    #    if store[3] in addresses:
    #        continue 
                
    #    addresses.append(store[3])
    #    logger.info(store)
       
       

    # return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
