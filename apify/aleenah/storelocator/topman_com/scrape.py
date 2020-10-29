
import csv
from sgselenium import SgSelenium
import re
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('topman_com')



driver = SgSelenium().chrome()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "raw_address"])
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

    urls=["https://www.topman.com/store-locator?country=Canada","https://www.topman.com/store-locator?country=United+States"]
    for url in urls:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        scripts = soup.find_all('script', {'type': 'application/ld+json'})
        if "Canada"  in url:
            for scr in scripts:
                countries.append("CA")
                tex=scr.text
                locs.append(re.findall(r'.*"name":"([^"]*)"', tex)[0])
                if "Regina" in locs:
                    k=0
                p= re.findall(r'.*"telephone":"([^"]*)"', tex)[0]
                if p == "":
                    phones.append("<MISSING>")
                else:
                    phones.append(p)
                tim = re.findall(r'.*"openingHours":"([^"]*)"',tex)[0]
                if tim=="":
                    timing.append("<MISSING>")
                else:
                    timing.append(tim)
                addr = re.findall(r'.*"addressLocality":"([^"]*)"',tex)
                if addr == []:
                    z = re.findall(r'.*"postalCode":"([^"]*)"', tex)
                    if z == []:
                        zips.append("<MISSING>")
                    else:
                        zips.append(z[0])
                    addr = re.findall(r'.*"streetAddress":"([^"]*)"', tex)[0]
                    states.append("<MISSING>")
                    cities.append("<MISSING>")
                    if addr == "":
                        street.append("<MISSING>")
                    else:
                        street.append(addr)

                    continue
                else:
                    addr=addr[0]
                z = re.findall(r'([ABCEGHJ-NPRSTVXY][0-9][ABCEGHJ-NPRSTV-Z] [0-9][ABCEGHJ-NPRSTV-Z][0-9])',addr)
                if z ==[]:
                    z=re.findall(r'.*"postalCode":"([^"]*)"', tex)
                    if z==[]:
                        zips.append("<MISSING>")
                    else:
                        zips.append(z[0])

                else:
                    zips.append(z[0])
                    addr = re.findall(r'.*"streetAddress":"([^"]*)"', tex)[0]
                    if addr =="":
                        states.append("<MISSING>")
                        street.append("<MISSING>")
                        cities.append("<MISSING>")
                        continue

                    add = addr.strip().split(",")
                    if add[-1] == "":
                        del add[-1]
                    s=re.findall(r'( [A-Z]{2}$)', add[-1])
                    if s==[]:
                        states.append("<MISSING>")
                    else:
                        states.append(add[-1].strip())
                        del add[-1]
                    cities.append(add[-1].strip())
                    del add[-1]
                    st=""
                    for a in add:
                        st+=(a+" ")
                    street.append(st.strip())
                    continue
                s=re.findall(r'([A-Z]{2}$)', addr)
                if s!=[]:
                    states.append(s[0])
                    addr = re.findall(r'.*"streetAddress":"([^"]*)"', tex)[0]
                    z=re.findall(r'([ABCEGHJ-NPRSTVXY][0-9][ABCEGHJ-NPRSTV-Z] [0-9][ABCEGHJ-NPRSTV-Z][0-9])', addr)
                    if z!=[]:
                        z=z[0]
                        addr=addr.replace(z,"")
                        zips[-1]=z
                    if addr == "":
                        states.append("<MISSING>")
                        street.append("<MISSING>")
                        cities.append("<MISSING>")
                        continue
                    add=addr.strip().split(",")
                    if add[-1]=="":
                        del add[-1]
                    cities.append(add[-1].strip())
                    del add[-1]
                    st = ""
                    for a in add:
                        st += (a + " ")
                    street.append(st.strip())
                    continue
                else:
                    cities.append(addr)
                    states.append("<MISSING>")
                    addr = re.findall(r'.*"streetAddress":"([^"]*)"', tex)[0]
                    if addr == "":
                        street.append("<MISSING>")
                    else:
                        street.append(addr)
            texts = re.findall(r'"stores":(.*),"selectedStore":', soup.text, re.DOTALL)[0].split('"cfsiPickCutOffTime"')
            del texts[-1]
            for tex in texts:
                ids.append(re.findall(r'.*"storeId":"([^"]*)"', tex)[0])
                la = re.findall(r'.*"latitude":(-?[\d\.]*)', tex)[0]
                lo = re.findall(r'.*"longitude":(-?[\d\.]*)', tex)[0]
                if la == "0":
                    lat.append("<MISSING>")
                else:
                    lat.append(la)
                if lo == "0":
                    long.append("<MISSING>")
                else:
                    long.append(lo)

        else:
            for scr in scripts:

                countries.append("US")
                tex=scr.text
                locs.append(re.findall(r'.*"name":"([^"]*)"', tex)[0])
                p = re.findall(r'.*"telephone":"([^"]*)"', tex)[0]
                if p == "":
                    phones.append("<MISSING>")
                else:
                    phones.append(p)
                tim = re.findall(r'.*"openingHours":"([^"]*)"', tex)[0]
                if tim == "":
                    timing.append("<MISSING>")
                else:
                    timing.append(tim)

                addr = re.findall(r'.*"addressLocality":"([^"]*)"', tex)
                if addr==[]:
                    cities.append("<MISSING>")
                else:
                    cities.append(addr[0])
                z = re.findall(r'.*"postalCode":"([^"]*)"', tex)
                if z == []:
                    zips.append("<MISSING>")
                else:
                    zips.append(z[0])
                states.append("<MISSING>")
                addr = re.findall(r'.*"streetAddress":"([^"]*)"', tex)[0]
                if addr =="":
                    street.append("<MISSING>")
                else:
                    street.append(addr)
            texts = re.findall(r'"stores":(.*),"selectedStore":', soup.text, re.DOTALL)[0].split('"cfsiPickCutOffTime"')
            del texts[-1]
            for tex in texts:
                ids.append(re.findall(r'.*"storeId":"([^"]*)"', tex)[0])
                la=re.findall(r'.*"latitude":(-?[\d\.]*)', tex)[0]
                lo=re.findall(r'.*"longitude":(-?[\d\.]*)', tex)[0]
                if la =="0":
                    lat.append("<MISSING>")
                else:
                    lat.append(la)
                if lo =="0":
                    long.append("<MISSING>")
                else:
                    long.append(lo)

    """
        divs = driver.find_elements_by_xpath("//div[@class='Store-headerDetails']")
        #diva= driver.find_element_by_xpath('//div[@class="StoreLocator-resultsContainer StoreLocator-resultsContainer--fullHeight"]')
        if "Canada" not in url:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            scripts = soup.find_all('script', {'type': 'application/ld+json'})

        logger.info(len(divs))
        for div in divs:
            if div.find_elements_by_class_name("Store-address") ==[]:        #assuming if no address associated either closed or havent started yet
                continue

            name = div.find_element_by_class_name("Store-name").text
            locs.append(name)

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
                    ad = ad.replace(e[-1], "")
                    z+= e[-1].strip(" ").strip(",")

                e = re.findall(r'( [A-Z]{2},)', ad)
                if e != []:
                    ad = ad.replace(e[-1], "")
                    s += e[-1].strip(" ").strip(",")

                ad=ad.strip(" ").strip(",")
                ad=re.sub(r'[\d ]+$', '', ad).split(",")

                if ad[-1] == "":
                    del a[-1]

                c+=ad[-1].strip()
                del ad[-1]
                for a in ad:
                    st+=a

                countries.append("CA")
                timing.append("<MISSING>")

            else:
                ad = ad.strip()

                e = re.findall(r'( [0-9]{5})', ad)
                if e != []:
                    ad = ad.replace(e[-1], "")
                    z += e[-1].strip(" ").strip(",")

                ad = ad.strip(" ").strip(",")
                ad = re.sub(r'[\d ]+$', '', ad).split(",")

                if ad[-1] == "":
                    del ad[-1]

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
    for scr in scripts:
            g = re.findall(r'.*"openingHours":"([^"]*)","',scr.text)[0]
            #logger.info(g)
            if g =="":
                timing.append("<MISSING>")
            else:
                timing.append(g)
    """
    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.topman.com")
        row.append(locs[i])
        row.append("<INACCESSIBLE>")
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append(countries[i])
        row.append(ids[i])  # store #
        row.append(phones[i]) #phone
        row.append("<MISSING>") #type
        row.append(lat[i]) #lat
        row.append(long[i]) #long
        row.append(timing[i])
        row.append(street[i])

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
