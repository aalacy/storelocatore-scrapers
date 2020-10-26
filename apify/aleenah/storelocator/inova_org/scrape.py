import csv
from sgselenium import SgSelenium
import re
from bs4 import BeautifulSoup

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
    ids=[]
    urls=[]
    types=[]
    """
    driver.get("https://www.inova.org/locations")
    #soup = BeautifulSoup(driver.page_source, 'html.parser')
    #divs= soup.find_all('div',{'class':'item'})
    divss = driver.find_element_by_id("mCSB_1_container")

    divs= divss.find_elements_by_class_name("item")

    print(len(divs))
    i=0
    for div in divs:
        
        locs.append(div.find_element_by_tag_name("h2").text)
        if i not in [0,2,3]:
            but = div.find_element_by_tag_name("button")
            but.click()

        print(locs[i])

        try:
            addr=(div.find_element_by_class_name("address").text)
        except:
            addr=""
            print(i)
        i += 1
        if addr != "":
            addr=addr.split("\n")
            addr=addr[-1].split(",")
            cities.append(addr[0])
            addr=addr[1].strip().split(" ")
            states.append(addr[0])
            zips.append(addr[1])
            del addr[-1]
            s=""
            for a in addr:
                s+=a
            street.append(s)
        else:
            print(i)
            cities.append("<INACCESSIBLE>")
            states.append("<INACCESSIBLE>")
            zips.append("<INACCESSIBLE>")
            street.append("<INACCESSIBLE>")
        try:
            p=(div.find_element_by_class_name("phone").text)
        except:
            p=""
        try:
            tim=(div.find_element_by_class_name("schedule").text)
        except:
            tim=""
        #p=div.find_element_by_class_name("phone").text
        if p !="":
            phones.append(re.findall(r'([0-9\-]+)', p)[0])
        else:
            phones.append("<MISSING>")
        #tim=div.find_element_by_class_name("schedule").text
        if tim !="":
            timing.append(tim)
        else:
            timing.append("<MISSING>")
            
        urls.append(div.find_element_by_tag_name("h2").find_element_by_tag_name("a").get_attribute("href"))

    for url in urls:
        driver.get(url)
        div = driver.find_element_by_id("block-inova-content").find_element_by_class_name("content")
        tex=div.text
        tex=tex.split("\n")
        locs.append(tex[0])

        del tex[0]
        if "Driving Directions" in tex:
            del tex[tex.index("Driving Directions")]
        ind=0
        p=0
        ad=0
        for i in tex:
            if re.findall(r'( [A-Z]{2})', i) != [] and "," in i:
                o=i
                i=i.split(",")
                cities.append(i[0])
                ad=1
                i=i[1].strip().split(" ")
                states.append(i[0])
                zips.append(i[1])
                ind= tex.index(o)

                continue
            elif "Phone: " in i:
                phones.append(re.findall(r'([0-9\-]+)', i)[0])
                del tex[tex.index(i)]
                p=1
                break
        if ad==0:
            cities.append("<MISSING>")
            states.append("<MISSING>")
            zips.append("<MISSING>")
        if p ==0:
            phones.append("<MISSING>")
        st=""
        for i in range(ind-1):
             st+=tex[i]
        if st =="":
            street.append("<MISSING>")
        else:
            street.append(st)
        try:
            di=driver.find_element_by_id("block-inova-content")
            di.find_element_by_class_name("current-status").click()
            times=di.find_elements_by_class_name("hours")
            tim=""
            for t in times:
                tim+=t.text+" "
            timing.append(tim.strip())
        except:
            timing.append("<MISSING>")
    """
    driver.get("https://www.inova.org/locations")

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    script = soup.find('script', {'type': 'application/json'})
    list=re.findall(r'"allResults":(.*)',script.text)[0]
    idss=list.split('"indexExtra"')
    del idss[-1]
    print(len(idss))

    for tex in idss:

        l = re.findall(r'.*"name":"([^"]*)"', tex)[0].replace("\n"," ")
        st=re.findall(r'.*"address_line1":"([^"]*)"', tex)[0]
        try:
            st += (" "+re.findall(r'.*"address_line2":"([^"]*)"', tex)[0])
        except:
            k=0
        c=re.findall(r'.*"locality":"([^"]*)"', tex)[0]
        la=re.findall(r'.*"lat":(-?[\d\.]*)', tex)
        if la ==[]:
            la="<MISSING>"
        else:
            la=la[0].strip()
        lo=re.findall(r'.*"lng":(-?[\d\.]*)', tex)
        if lo ==[]:
            lo="<MISSING>"
        else:
            lo=lo[0].strip()
        try:
            p=re.findall(r'.*"phone":"([^"]*)"', tex,re.DOTALL)[0].strip()
            p=re.sub(r'[A-Z]+',"",p)

        except:
            p="<MISSING>"
        z=re.findall(r'.*"postal_code":"([^"]*)"', tex)[0].strip()
        s=re.findall(r'.*"administrative_area":"([^"]*)"', tex)[0].strip()
        if s=="":
            s="<MISSING>"
        id=re.findall(r'.*"id":"([^"]*)"', tex)[0]
        tim=re.findall(r'.*"schedule":\{(.*)\},"direction', tex, re.DOTALL)[0].strip().replace("\"","").replace("{","").replace("}","").replace("\n"," ").replace("null"," ")

        ltypes=re.findall(r'.*"locationTypes":(.*),"address"', tex,re.DOTALL)[0].strip()
        if ltypes =="[]":
            locs.append(l)
            states.append(s)
            cities.append(c)
            zips.append(z)
            timing.append(tim)
            street.append(st)
            lat.append(la)
            long.append(lo)
            phones.append(p)
            ids.append(id)
            types.append("<MISSING>")
        else:
            subs = ltypes.split("},{")
            for sub in subs:
                id = re.findall(r'.*"id":"([^"]*)"', tex)[0]
                t=re.findall(r'.*"name":"([^"]*)"', tex)[0]
                locs.append(l)
                states.append(s)
                cities.append(c)
                zips.append(z)
                timing.append(tim)
                street.append(st)
                lat.append(la)
                long.append(lo)
                phones.append(p)
                ids.append(id)
                types.append(t)

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.inova.org")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append(ids[i])  # store #
        row.append(phones[i])  # phone
        row.append(types[i])  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i]) #timing
        if row not in all:
            all.append(row)
        
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
