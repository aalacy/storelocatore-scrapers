import csv
from sgselenium import SgSelenium
import re
#import reverse_geocoder
#from slimit.parser import Parser

driver = SgSelenium().chrome()

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
    links=[]

    driver.get("https://www.spiritofmath.com/campuses/")
    uls=driver.find_element_by_class_name('res-con').find_elements_by_tag_name('ul')

    for i in range(len(uls)):
        li = uls[i]
        tex=li.text.split("\n")
        if tex[0]=="Head Office":
            continue
        addr=tex[1]

        if "Pakistan" in addr:
            continue

        e = re.findall(r'( [ABCEGHJ-NPRSTVXY][0-9][ABCEGHJ-NPRSTV-Z] [0-9][ABCEGHJ-NPRSTV-Z][0-9])', addr) #canadian zip
        if e != []:
            addr = addr.replace(e[0], "")
            zips.append(e[0].strip())
            countries.append("CA")
        else:
            e = re.findall(r'( [0-9]{5})', addr) #american zip
            if e != []:
                addr = addr.replace(e[0], "")
                zips.append(e[0].strip())
                countries.append("US")
            else:
                zips.append("<MISSING>")
                countries.append("<MISSING>")

        e = re.findall(r'.*( [A-Z]{2}[ \,]*)$', addr)
        if e != []:
            addr = addr.replace(e[0], "")
            states.append( e[0].strip().strip(","))
        else:
            e = re.findall(r'.*( Ontario[ \,]*)$', addr)
            if e != []:
                addr = addr.replace(e[0], "")
                states.append(e[0].strip().strip(","))
            else:
                states.append("<MISSING>")
        addr=addr.strip().strip(",")
        o =addr.split(",")[-1].strip()
        addr=addr.replace(o,"").strip().strip(",")
        cities.append(o)
        street.append(addr)
        locs.append(tex[0])
        e=re.findall(r'([0-9\-]+.*)', tex[2].strip())
        if e != []:
            phones.append(e[0].replace("MATH ",""))
        else:
            phones.append("<MISSING>")
        links.append(li.find_element_by_tag_name("a").get_attribute("href"))

    for link in links:
        print(link)
        driver.get(link)
        try:
            news=driver.find_element_by_xpath('//div[@class="news-text"]').text
        except:
            try:
                news = driver.find_element_by_class_name("news-text").text
            except:

                h=driver.page_source
                if 'Mon' in h:

                    news=re.findall(r'(Mon.*by appointment only)',h,re.DOTALL)[0].replace('<li style="text-align: left">',' ').replace('</li>','').replace('</b></span></p>','').replace('<ul>','')
                else:
                    news=''
        #print(news)
        try:
            tim = re.findall(r'(Hours.*pm|HOURS.*pm|Hours.*PM|HOURS.*PM).*(Open)*(OPEN)*',news,re.DOTALL)[0][0].replace("\n"," ")
            try:
                tim=tim.replace(re.findall(r'pm|PM(.*Open.*)',tim,re.DOTALL)[0],"")
            except:
                tim=tim
            print (tim)
            timing.append(tim)
        except:
            timing.append("<MISSING>")

    """ 
    links.append(li.find_element_by_tag_name("a").get_attribute("href"))
    to extract lat long and country
    for link in links:
        driver.get(link)
        div=driver.find_element_by_class_name("popup-holder")
        scripts= div.find_elements_by_css_selector("script")
        parser=Parser()
        tex=""
        for s in scripts:
            tex+=s.text
        print(tex)
        la= re.findall(r'var myLatLng = {lat: (.*),',tex)[0]
        lat.append(la)
        lo= re.findall(r'var myLatLng = {lat: .* lng: (.*)}',tex)[0]
        long.append(lo)
        cord=(la,lo)
        countries.append(reverse_geocoder.search(cord)[0]["cc"])
    """

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.spiritofmath.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append(countries[i])
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<INACCESSIBLE>")  # type
        row.append("<INACCESSIBLE>")  # lat
        row.append("<INACCESSIBLE>")  # long
        row.append(timing[i])    #timing

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
