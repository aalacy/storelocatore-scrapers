
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re


options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r'll=[-?\d\.]*\,([-?\d\.]*)', url)[0]
    lat = re.findall(r'll=(-?[\d\.]*)', url)[0]
    return lat, lon


def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states=[]
    cities = []
    countries=[]
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    urls=["https://www.topman.com/store-locator?country=Canada","https://www.topman.com/store-locator?country=United+States"]
    for url in urls:
        driver.get(url)
        divs = driver.find_elements_by_xpath("//div[@class='Store-headerDetails']")
        print(len(divs))
        for div in divs:
            if div.find_elements_by_class_name("Store-address") ==[]:        #assuming if no address associated either closed or havent started yet
                continue

            name = div.find_element_by_class_name("Store-name").text
            locs.append(name)

            tim = div.find_element_by_class_name("Store-openNowInfo").text
            if tim =="":
                timing.append("<Missing>")
            else:
                timing.append(tim.strip())

            ad = div.find_element_by_class_name("Store-address").text
            #ad=ad.split(",")
            st=""
            c=""
            s=""
            z=""
            if"Canada" in url:
                ad=ad.strip()

                e = re.findall(r'( [ABCEGHJ-NPRSTVXY][0-9][ABCEGHJ-NPRSTV-Z] [0-9][ABCEGHJ-NPRSTV-Z][0-9])',ad)
                if e!= []:
                    ad = ad.replace(e[0], "")
                    z+= e[0].strip(" ").strip(",")

                e = re.findall(r'( [A-Z]{2},)', ad)
                if e != []:
                    ad = ad.replace(e[0], "")
                    s += e[0].strip(" ").strip(",")

                ad=ad.strip(" ").strip(",").split(",")

                if ad[-1] == "":
                    del a[-1]
                c+=ad[-1].strip()
                del ad[-1]
                for a in ad:
                    st+=a

                countries.append("CA")

            else:
                ad = ad.strip()

                e = re.findall(r'( [0-9]{5})', ad)
                if e != []:
                    ad = ad.replace(e[0], "")
                    z += e[0].strip(" ").strip(",")

                ad = ad.strip(" ").strip(",").split(",")

                if ad[-1] == "":
                    del a[-1]
                c += ad[-1].strip()
                del ad[-1]
                for a in ad:
                    st += a
                countries.append("US")

            if c == "":
                cities.append("<MISSING>")
            else:
                cities.append(c)
            if s == "":
                states.append("<MISSING>")
            else:
                states.append(s)
            if z == "":
                zips.append("<MISSING>")
            else:
                zips.append(z)
            if st == "":
                street.append("<MISSING>")
            else:
                street.append(st)

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.topman.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append(countries[i])
        row.append("<MISSING>")  # store #
        row.append("<MISSING>") #phone
        row.append("<MISSING>") #type
        row.append("<MISSING>") #lat
        row.append("<MISSING>") #long
        row.append(timing[i])

        all.append(row)
    return all



def scrape():
    data = fetch_data()
    write_output(data)

scrape()