import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('ginoseast_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    return_main_object=[]
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.ginoseast.com"
    r = session.get("https://www.ginoseast.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for data in soup.find("div",{"id":"page-5db3337c9f175d60ba85158a"}).find_all("h3"):
        for link in data.find_all("a"):            
            page_url = "https://www.ginoseast.com"+link['href']
            r1 = session.get(page_url,headers=headers)
            # logger.info(page_url)
            soup1 = BeautifulSoup(r1.text,"lxml")
            name = soup1.h1.text.strip()
            full = list(soup1.find_all("div",{"class":"col sqs-col-6 span-6"})[1].find("div",{"class":"row sqs-row"}).stripped_strings)
            phone = full[-1]
            if "coming soon" in phone.lower():
                continue
            city = full[-3].split(',')[0]
            state = full[-3].split(',')[1].strip().split( )[0]
            zipcode= full[-3].split(',')[1].strip().split( )[-1]
            if zipcode == "60665":
                zipcode = "60605"
            street = full[-4]
            hours = " ".join(full[1:-5])
            if not hours:
                hours = "<MISSING>"
            store=[]
            store.append("https://www.ginoseast.com")
            store.append(name)
            store.append(street)
            store.append(city)
            store.append(state)
            store.append(zipcode.replace("CA","<MISSING>"))
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(hours.replace('Delivery & Curbside Pick-Up available ','').replace(' Delivery available after 5pm',''))
            store.append(page_url)
            yield store
            #logger.info(store)
            




    # exit()
    # main_link = "https:" + soup.find_all("iframe")[-1]["src"]
    # logger.info(main_link)
    # exit()
    # api_key = main_link.split("api_key=")[1].split("&")[0]
    # main_request  = session.get("https://app.mapply.net/front-end//get_surrounding_stores.php?api_key=" + api_key + "&latitude=40.627687485975684&longitude=-85.975110686635&max_distance=0&limit=10000&calc_distance=0",headers=headers)
    # return_main_object = []
    # data = main_request.json()["stores"]
    # for i in range(len(data)):
    #     store_data = data[i]
    #     store = []
    #     details_soup = BeautifulSoup(store_data["detailed"],"lxml")
    #     name = details_soup.find("span",{"class":"name"}).text
    #     street = details_soup.find("span",{"class":"address"}).text
    #     city = details_soup.find("span",{"class":"city"}).text
    #     state = details_soup.find("span",{"class":"prov_state"}).text
    #     postal_zip = details_soup.find("span",{"class":"postal_zip"}).text
    #     if details_soup.find("span",{"class":"phone"}) == None:
    #         phone = "<MISSING>"
    #     else:
    #         phone = details_soup.find("span",{"class":"phone"}).text[1:]

    #     location_url = details_soup.find_all("a")[-1]
    #     hours = ""
    #     if location_url["href"] == "":
    #         pass
    #     else:
    #         location_request = session.get(location_url["href"],headers=headers)
    #         lcoation_soup = BeautifulSoup(location_request.text,"lxml")
    #         store_hours = list(lcoation_soup.find("div",{"id":"ctl01_rptSpan_ctl01_pText"}).stripped_strings)[:-1]
    #         for k in range(len(store_hours)):
    #             if "Hours of Operation:" in store_hours[k]:
    #                 hours = " ".join(store_hours[k+1:])
    #     store.append("https://www.ginoseast.com")
    #     store.append(name)
    #     store.append(street)
    #     store.append(city)
    #     store.append(state)
    #     store.append(postal_zip)
    #     store.append("US")
    #     store.append(store_data["store_id"])
    #     store.append(phone)
    #     store.append("gino's east")
    #     store.append(store_data["lat"])
    #     store.append(store_data["lng"])
    #     store.append(hours if hours != "" else "<MISSING>")
    #     return_main_object.append(store)
    # return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
