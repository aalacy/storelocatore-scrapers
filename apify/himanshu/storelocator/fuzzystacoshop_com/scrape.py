import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('fuzzystacoshop_com')






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
        return str(hour) + ":" + k1 + " " + am
        


def fetch_data():
    # zips = sgzip.for_radius(100)
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 1000000
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()
    addresses = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',

    }

    # it will used in store data.
    while coord:
        result_coords = []
        lat = coord[0]
        lng = coord[1]
        #logger.info(lng)
        try:
            r = session.get(
            'https://www.fuzzystacoshop.com/locations/?gmw_form=1&gmw_per_page=3000&gmw_lat='+str(lat)+'&gmw_lng='+str(lng)+'&gmw_px=pt&action=gmw_post',
            headers=headers)
        except:
            continue
        soup1= BeautifulSoup(r.text,"lxml")
        
        if soup1 != None:
            # k = soup1.find("script",{"type":"text/javascript","id":"locsJson"}).text.split("var locations =")[1].split("jQuery")[0].replace(";","")
            v3 =soup1.find("script",{"type":"text/javascript","id":"locsJson"})
        
            if v3 != None:
                # page = (soup1.find("a",{"class":"Btn Btn--pink LocationsMap-linksBtn"})['href'])
                k = v3.text.split("var locations = ")[1].split("jQuery")[0].replace(";","")
                # logger.info("======================out side of =============",json.loads(k))
                k1 = json.loads(k)
                current_results_len = len(k)
                #logger.info("current_results_len===================== ",current_results_len)
                for i in k1:
                    name = i['title']
                    lat = i['lat']
                    log = i["lng"]

                    h1= BeautifulSoup(i['hours'],"lxml")
                    k2=(h1.find_all("td"))
                    if k2 !=[]:
                        v1= (list(h1.stripped_strings))
                        pie = 0
                        v2 = [p.replace("&nbsp&nbsp&ndash&nbsp&nbsp","") for p in v1]
                        for index,j in enumerate(v2,start=0):
                            if "/" in j:
                                del v2[index]
                        time = " ".join(v2)
                  
                    else:
                        time = "<MISSING>"
                    tem_var=[]
                    result_coords.append((lat, log))
                    tem_var.append("https://www.fuzzystacoshop.com")
                    tem_var.append(name if name  else "<MISSING>")
                    tem_var.append(i['address'] if i['address']  else "<MISSING>")
                    tem_var.append(i["city"] if i["city"] else "<MISSING>")
                    tem_var.append(i['state'] if i['state'] else "<MISSING>" )
                    if i['zipcode']=="0":
                        tem_var.append("<MISSING>")
                    else:
                        tem_var.append(i['zipcode'] if i['zipcode'] else "<MISSING>")
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append(i["phone"] if i['phone'] else "<MISSING>" )
                    tem_var.append("<MISSING>")
                    tem_var.append(lat if lat else "<MISSING>" )
                    tem_var.append(i["lng"] if i["lng"] else  "<MISSING>")
                    tem_var.append(time if time else "<MISSING>")
                    tem_var.append("<MISSING>")
                    if tem_var[2] in addresses:
                        continue
                    addresses.append(tem_var[2])
                    match = re.search(r'\b(COMING SOON)\b',tem_var[1])
                    if match:
                        pass
                    else:
                        yield tem_var
                        #logger.info(tem_var)
                    #logger.info("======================================")


        if current_results_len < MAX_RESULTS:
            #logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            #logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()
                   
     


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
