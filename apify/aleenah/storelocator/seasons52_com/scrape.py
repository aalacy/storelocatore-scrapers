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
        writer.writerow(["locator_domain","operating_info", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r'll=[-?\d\.]*\,([-?\d\.]*)', url)[0]
    lat = re.findall(r'll=(-?[\d\.]*)', url)[0]
    return lat, lon


def fetch_data():
    # Your scraper here
    abv= {'alabama': 'AL','arizona': 'AZ','california': 'CA','colorado': 'CO','florida': 'FL','georgia': 'GA','illinois': 'IL','indiana': 'IN','maryland': 'MD','massachusetts': 'MA','michigan': 'MI','missouri': 'MO','new jersey': 'NJ','new mexico': 'NM','new york': 'NY','north carolina': 'NC','ohio': 'OH','pennsylvania': 'PA','tennessee': 'TN','texas': 'TX','virginia': 'VA',}
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
    ulinks=[]
    gms=[]
    urls=[]
    driver.get("https://www.seasons52.com/locations/all-locations")
    div=driver.find_element_by_class_name("fin_all_location_sec")
    uls=div.find_elements_by_css_selector("ul")
    for ul in uls:
        lis= ul.find_elements_by_css_selector("li")
        s=""
        for li in lis:
            h=li.get_attribute("class")
            if h == "heading_li":
               s=li.text
               continue
            elif h== "subheading_li":
                l=li.text
            states.append(s)
            locs.append(l)
    ast=driver.find_elements_by_tag_name("a")
    for a in ast:
        if a.get_attribute("id")=="locDetailsId":
            urls.append(a.get_attribute("href"))
    i=0

    for url in urls:
        """
        loc=loc.lower()
        if "-" in loc:
            lo = loc.split("-")
            loc1=lo[0].strip().replace(" ","-")
            loc2=loc.replace("- ","").replace(" ","-")
        else:
            if " " in loc:
                loc1=loc.replace(" ","-")
                loc2=loc1
            else:
                loc1=loc2=loc
        url="https://www.seasons52.com/locations/"+abv[states[i].lower()]+"/"+loc1+"/"+loc2
        """
        driver.get(url)
        div = driver.find_element_by_class_name("left-bar")
        try:
            gm=driver.find_element_by_id("globalMessage").text.replace("\r\n"," ").replace("\n"," ").strip()
        except:
            gm="<MISSING>"
        print(gm)
        gms.append(gm)
        p=div.find_element_by_tag_name("p")
        t=p.text.split("\n")
        street.append(t[0])
        phones.append(t[2])
        t=t[1].split(",")
        cities.append(t[0])
        zips.append(t[1].split(" ")[-1])
        i+=1
        lis=driver.find_elements_by_css_selector("li")
        tim=""
        for lin in lis:
            id = lin.get_attribute("class")
            if id =="weekday-active rolling-width" or id=="time rolling-hours-start"or id=="weekday rolling-width":
                tim+=lin.text
        timing.append(tim.replace("FRI SEP 20","").replace("EDT 2019",""))
        latlong=driver.find_element_by_id("restLatLong").get_attribute("value").split(",")
        lat.append(latlong[0])
        long.append(latlong[1])


    all = []
    for i in range(0, len(locs)):
        row=[]
        row.append("https://www.seasons52.com")
        row.append(gms[i])
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])

        all.append(row)
    return(all)
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
