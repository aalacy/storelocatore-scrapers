import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('goodyearctsc_com')

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
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
        return str(hour) + ":" + str(int(str(time / 60).split(".")[1]) * 6) + " " + am


def fetch_data():
    # zips = sgzip.for_radius(100)
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()
    MAX_RESULTS = 100000
    MAX_DISTANCE = 250
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()

    return_main_object = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    address=[]
    while coord:
        result_coords = []

        lat = coord[0]
        lng = coord[1]
        r = session.get(
            'https://gyfleethqservices.com/api/Dealer/DealerSearch?dealerSearchParameters.milesRadius='+str(MAX_DISTANCE)+'&dealerSearchParameters.latitude='+str(lat)+'&dealerSearchParameters.longitude='+str(lng)+'&api_key=vdUHnhNUY95w3OiVgugndw7Z2VGwBkUgTaQuLozc35gj2alKoaKbk3yKWFm5Edjy8tTJSYXO94K+9UnjaJBUnw==',
            headers=headers,
        )
        # logger.info( 'https://gyfleethqservices.com/api/Dealer/DealerSearch?dealerSearchParameters.milesRadius=250&dealerSearchParameters.latitude='+str(lat)+'&dealerSearchParameters.longitude='+str(lng)+'&api_key=vdUHnhNUY95w3OiVgugndw7Z2VGwBkUgTaQuLozc35gj2alKoaKbk3yKWFm5Edjy8tTJSYXO94K+9UnjaJBUnw==')
        soup= BeautifulSoup(r.text,"lxml")
        k = json.loads(soup.text)
        time =''
        if k != None and k !=[]:
            # logger.info("=============================")
            current_results_len = len(k)
            for i in k:
                tem_var=[]
                if 'hours' in i and i['hours'] !=None:
                    for j in i['hours']:
                        time = time +' ' +(j['day']+ ' '+j['formattedTime'])
                else:
                    time = ''
                tem_var.append("https://www.goodyearctsc.com")
                tem_var.append(i['name'] if i['name'] else "<MISSING>" )
                if i['streetAddress'].strip() == "--":
                    tem_var.append("<MISSING>" )
                else:
                    tem_var.append(i['streetAddress'].strip() if i['streetAddress'].strip()  else "<MISSING>" )
                tem_var.append(i['city'].strip() if i['city'].strip() else "<MISSING>")
                tem_var.append(i['state'] if i['state'] else "<MISSING>")
                if len(i['zip'])==6 or len(i['zip'])==7:
                    c = 'CA'
                else:
                    c = "US"
                tem_var.append(i['zip'] if i['zip'] else "<MISSING>")
                tem_var.append(c)
                tem_var.append("<MISSING>")
                tem_var.append(i['phoneFormatted'] if i['phoneFormatted'] else "<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(i['geoLocation']['latitude'] if i['geoLocation']['latitude'] else "<MISSING>" )
                tem_var.append(i['geoLocation']['longitude'] if i['geoLocation']['longitude'] else "<MISSING>" )
                tem_var.append(time if time else "<MISSING>" )
                latitude = i['geoLocation']['latitude'] 
                longitude = i['geoLocation']['longitude']
                tem_var.append("<MISSING>")
                result_coords.append((latitude, longitude))
                if tem_var[2] in addresses:
                    continue
                addresses.append(tem_var[2])

                yield tem_var
            # logger.info("===================================================")
        if current_results_len < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)


scrape()



