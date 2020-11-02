import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('fiatusa_com')






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
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 300
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()
  

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Accept": "/",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    # it will used in store data.
    locator_domain = "https://www.fiatusa.com"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "drmartens"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    address=[]
    while zip_code:
        result_coords = []
        # logger.info("zips === " + str(zip_code))

        r = session.get(
            'https://www.fiatusa.com/bdlws/MDLSDealerLocator?brandCode=X&func=SALES&radius='+str(MAX_DISTANCE)+'&resultsPage=1&resultsPerPage='+str(MAX_RESULTS)+'&zipCode='+zip_code
        )
        soup= BeautifulSoup(r.text,"lxml")
        k = json.loads(soup.text)
        if 'dealer' in k:
            current_results_len = len(k)
            for i in k['dealer']:
                tem_var=[]
                st = i['dealerAddress1']
                # logger.info(st)
                # logger.info(i['departments']['sales']['hours']['sunday']['open']['time'] + ' '+i['departments']['sales']['hours']['sunday']['close']['time'])
                hours = 'sunday' +' '+i['departments']['sales']['hours']['sunday']['open']['time'].replace("0:00 0:00","Close") + ' '+i['departments']['sales']['hours']['sunday']['close']['time']+ ' '+'monday'+' '+i['departments']['sales']['hours']['monday']['open']['time'] + ' '+i['departments']['sales']['hours']['monday']['close']['time']+ ' '+ 'tuesday'+' '+i['departments']['sales']['hours']['tuesday']['open']['time'] + ' '+i['departments']['sales']['hours']['tuesday']['close']['time']+' '+'wednesday'+' '+i['departments']['sales']['hours']['wednesday']['open']['time'] + ' '+i['departments']['sales']['hours']['wednesday']['close']['time']+' '+'thursday'+' '+i['departments']['sales']['hours']['thursday']['open']['time'] + ' '+i['departments']['sales']['hours']['thursday']['close']['time']+' '+'friday'+' '+i['departments']['sales']['hours']['friday']['open']['time'] + ' '+i['departments']['sales']['hours']['friday']['close']['time']+ ' '+'saturday'+' '+i['departments']['sales']['hours']['saturday']['open']['time'] + ' '+i['departments']['sales']['hours']['saturday']['close']['time']
                if len(i['dealerZipCode'])==6 or len(i['dealerZipCode'])==7:
                    c = "CA"
                else:
                    c= "US"
                if  len(i['dealerZipCode'])==9:
                    word = i['dealerZipCode']
                    index = 5
                    char = '-'
                    zip1 = word[:index] + char + word[index + 1:]
                  

                tem_var.append("https://www.fiatusa.com")
                tem_var.append(i['dealerName'])
                tem_var.append(st)
                tem_var.append(i['dealerCity'])
                tem_var.append(i['dealerState'])
                tem_var.append(zip1)
                tem_var.append(c)
                tem_var.append("<MISSING>")
                tem_var.append(i['phoneNumber'])
                tem_var.append("<MISSING>")
                tem_var.append(i['dealerShowroomLatitude'])
                tem_var.append(i['dealerShowroomLongitude'])
                tem_var.append(hours.replace("0:00 0:00","Close"))
                tem_var.append("<MISSING>")
                result_coords.append((i['dealerShowroomLatitude'], i['dealerShowroomLongitude']))
                # logger.info(tem_var)
                if tem_var[2] in addresses:
                    continue
                addresses.append(tem_var[2])
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

        

def scrape():
    data = fetch_data()
    write_output(data)


scrape()



