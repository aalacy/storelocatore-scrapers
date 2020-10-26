import csv
import re
from sgselenium import SgSelenium
from bs4 import BeautifulSoup
from pyzipcode import ZipCodeDatabase

driver = SgSelenium().chrome()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            try:
                writer.writerow(row)
            except:
                row[-2]=row[-2].replace("\u0335","")
                writer.writerow(row)

def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states=[]
    cities = []
    types=[]
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids=[]
    page_url=[]
    urls=[]
    driver.get("https://sunrisedental.com/directory/locations/all-locations")
    sa=driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[1]/div/article/div/div/div[2]/div[2]/div/div[2]/div[4]/div[2]/div").find_elements_by_tag_name("a")
    for a in sa:
        if re.findall(r'[0-9]+',a.text) !=[]:
            urls.append("https://sunrisedental.com/directory/locations/all-locations?p="+a.text)
    #urls=["https://sunrisedental.com/directory/locations/all-locations?p=1","https://sunrisedental.com/directory/locations/all-locations?p=2","https://sunrisedental.com/directory/locations/all-locations?p=3"]

    for url in urls:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        div=soup.find('div',{'class':'sabai-directory-listings sabai-directory-listings-list'})
        script=div.find('script',{'type':'text/javascript'}).text

        #print(div.text)
        #divs=div.fnd_all('div',{'class':'sabai-entity sabai-entity-type-content sabai-entity-bundle-name-directory-listing sabai-entity-bundle-type-directory-listing sabai-entity-mode-summary sabai-clearfix sabai-directory-no-image'})
        #print(len(divs))

        lat += re.findall(r'"lat":(-?[\d\.]*)', script)
        long += re.findall(r'"lng":(-?[\d\.]*)', script)
        lids = re.findall(r'"#sabai-entity-content-([0-9]+) .sabai-directory-title', script)
        ids+=lids

        print(len(lids))
        for id in lids:

            div = driver.find_element_by_id('sabai-entity-content-'+id)
            #div = div.find('div', {'class': "sabai-entity sabai-entity-type-content sabai-entity-bundle-name-directory-listing sabai-entity-bundle-type-directory-listing sabai-entity-mode-summary sabai-clearfix sabai-directory-no-image"})
            urll = div.find_element_by_class_name('sabai-directory-title').find_element_by_tag_name("a").get_attribute("href")
            page_url.append(urll)

            locs.append(div.find_element_by_class_name('sabai-directory-title').text)
            addr= div.find_element_by_class_name('sabai-directory-location').text.replace(", USA","").replace(", United States","")
            addr=addr.split(",")
            z = re.findall(r'[0-9]{5}', addr[-1].strip())
            if z == []:
                zips.append("<MISSING>")
                states.append(addr[-1].strip())
                cities.append(addr[-2].split(" ")[-1])

            else:
                z=z[0]
                zips.append(z)
                states.append(addr[-1].replace(z, ""))
                zcdb = ZipCodeDatabase()
                c=zcdb[z].place
                if c in addr[-2]:
                    cities.append(c)
                    addr[-2]=addr[-2].replace(c,"")
                else:
                    cities.append(addr[-2].split(" ")[-1])
            del addr[-1]
            st=""
            for a in addr:
                st+=a
            street.append(st)
            phones.append(div.find_element_by_class_name('sabai-directory-contact-tel').text)

    for url in page_url:

            driver.get(url)
            
            try:
                tim = driver.find_element_by_id('sabai-entity-content-'+ids[page_url.index(url)]).find_element_by_class_name("sabai-directory-body").text
                timing.append(re.findall(r'(.*pm)',tim,re.DOTALL)[0].replace("\n"," "))
            except:
                timing.append("<MISSING>")

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://sunrisedental.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append(ids[i])  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
