import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('levelsbarbershop_com')





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


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url = "https://www.levelsbarbershop.com/locations.html"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    store_name = []
    address =[]
    store_detail = []
    return_main_object = []
    hours = []
    phone = []

    k =  soup.find_all('div',{'class':'paragraph'})
    k1 = soup.find_all("h2", {"class": "wsite-content-title"})
    gk = []
    for index, target_list in enumerate(k1):

        gk.append(target_list.text.split(',')[0])


    i = 0
    check = []
    for target_list in k:
        locator_domain = 'https://www.levelsbarbershop.com/'
        check.append(gk[i])
        location_name = gk[i]
        tem_var = []
        latitude = ''
        longitude = ''

        if target_list.find('a') != None:
            latitude = (target_list.find('a')['href'].split("@")[1].split(',')[0])
            longitude = (target_list.find('a')['href'].split("@")[1].split(',')[1])



        if len(target_list.text.split(',')) != 1:
            if len(target_list.text.split(',')):

                street_address = (target_list.text.split(',')[0])
                city = (target_list.text.split(',')[1])

                state = (target_list.text.split(',')[2].split(',')[0].replace("\xa0", " ").split("Ph:")[0])

                phone = (target_list.text.split(',')[2].split(',')[0].replace("\xa0", " ").split("Ph:")[1])

                tem_var.append(locator_domain)
                tem_var.append(location_name.capitalize())
                tem_var.append(street_address)
                tem_var.append(city)
                tem_var.append(state.strip())
                tem_var.append("<MISSING>")
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("<MISSING>")
                tem_var.append(latitude)
                tem_var.append(longitude)
                tem_var.append("<MISSING>")
                tem_var.append("https://www.levelsbarbershop.com/locations.html")
                # logger.info("data== ", str(tem_var))

                yield tem_var
            i += 1
    mm =  soup.find_all('h2',{'class':'wsite-content-title'})[-7:-3]
    for i in mm:
        tem_var =[]
        if "MADISON AVE, NYC" in i.text or  "NOSTRAND AVENUE, NYC" in i.text:
            location_name = i.text
        else:
            city = i.text.split(",")[0].split(' ')[-1]
            street_address = " ".join(i.text.split(",")[0].split(' ')[:-1])
            state = i.text.split(",")[-1].replace("\xa0","").split("ph:")[0]
            phone = i.text.split(",")[-1].replace("\xa0","").split("ph:")[1]
        
        tem_var.append(locator_domain)
        tem_var.append(location_name)
        tem_var.append(street_address)
        tem_var.append(city)
        tem_var.append(state.strip())
        tem_var.append("<MISSING>")
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append("https://www.levelsbarbershop.com/locations.html")
        
        if tem_var[2] in address:
            continue
        
        address.append(tem_var[2])
        if "266 Windsor Hwy" in tem_var:
            pass
        else:
            yield tem_var
            # logger.info(tem_var)



def scrape():
    data = fetch_data()
    write_output(data)


scrape()


