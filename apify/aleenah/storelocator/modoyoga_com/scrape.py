import csv
import re
from bs4 import BeautifulSoup
import requests
from sgselenium import SgSelenium

driver = SgSelenium().chrome(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36")
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
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
    countries=[]
    urls=[]
    count=[]
    checks=[]
    headers={'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
'accept-encoding': 'gzip, deflate, br',
'accept-language': 'en-US,en;q=0.9',
        'sec-fetch-mode': 'navigate',
'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36'}
    res=requests.get("https://ndg.modoyoga.com/search-results/?userLocation=canada&studioLat=&studioLng=",headers=headers)
    data=res.text.split('<div class="marker" style="visibility')
    del data[0]
    for d in data:
        if "usa" in d.lower():
            if re.findall(r'<h5><a href="([^"]*)"', d)[0].strip() not in urls:
                urls.append(re.findall(r'<h5><a href="([^"]*)"', d)[0].strip())
                count.append("US")

        elif "canada" in d.lower():
            if re.findall(r'<h5><a href="([^"]*)"', d)[0].strip() not in urls:
                urls.append(re.findall(r'<h5><a href="([^"]*)"', d)[0].strip())
                count.append("CA")
        else:
            #checks.append(re.findall(r'<h5><a href="([^"]*)"', d)[0].strip())
            if re.findall(r'<h5><a href="([^"]*)"', d)[0].strip() not in urls:
                urls.append(re.findall(r'<h5><a href="([^"]*)"', d)[0].strip())
                count.append("<MISSING>")

    '''for check in checks:
        print(check)
        res = requests.get(check, headers=headers)
        #soup = BeautifulSoup(res.text, 'html.parser')
        if "canada" in res.text.lower():
            print('found canada')
        elif "usa" in res.text.lower():
            print('found usa')'''

    print("here",len(urls))
    for url in urls:
        cont=0
        res=requests.get(url,headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        print(url)

        driver.get(url)
        # print(driver.page_source)
        contacts = driver.find_elements_by_tag_name("section")

        for c in contacts:
            if c.get_attribute('id') == "contact":
                f = c.find_elements_by_tag_name("iframe")[1]
                driver.switch_to.frame(f)
                script = driver.find_element_by_xpath('//script[contains(text(), "onEmbedLoad")]')
                script_src = script.get_attribute('innerHTML')
                if "canada" in script_src.lower():
                    count[urls.index(url)]="CA"
                    #print("canada")
                elif "usa" in script_src.lower():
                    count[urls.index(url)] = "US"
                    #print("usa")
                else:
                    cont = 1
                    break

                lat_lng = re.search(r'(-\d+\.\d+), ?(\d+\.\d+)', script_src)
                la = lat_lng.group(2)
                lng = lat_lng.group(1)
                lat.append(la)
                long.append(lng)
                driver.switch_to.default_content()
                #print(la, lng)
        if cont ==1:
            continue
        divs = soup.find_all('div', {'class': 'col-6 offset-1'})
        for div in divs:

            locs.append(div.find('h2').text.strip())
            ps=div.find_all('p')
            p=ps[0].text
            p=re.sub(r'\([a-zA-Z \.]+\)',"",p)
            z = re.findall(r'[A-Z][0-9][A-Z] [0-9][A-Z][0-9]' , p,re.DOTALL)
            if z == []:
                z = re.findall(r'[0-9]{5}', p,re.DOTALL)

                if z == []:
                    z="<MISSING>"
                else:
                    z=z[0]
                    p = p.split(z)[0].strip()
            else:
                z=z[0]
                p = p.split(z)[0].strip()
            zips.append(z)
            s= re.findall(r'[A-Z]{2}', p,re.DOTALL)
            if s==[]:
                s="<MISSING>"
            else:
                s=s[-1]
                p = p.split(s)[0].replace(".","").strip()
            p=p.replace(", ,",",").replace(",,",",").strip()
            if "," in p.split("\n")[-1]:
                c=p.split("\n")[-1].split(",")[0].strip()
            else:
                c=p.split("\n")[-1].strip()
            if s=="<MISSING>":
                try:
                    s = p.split("\n")[-1].split(",")[1].strip()
                    p = p.replace(s,"").strip()
                except:
                    s = "<MISSING>"
                if s=="":
                    s = "<MISSING>"
            st= p.split(c)[0].replace(",","").replace("\r\n"," ").replace("\n"," ").strip()
            #print(st)
            if len(c)>2 and st=="":
                st=c
                c="<MISSING>"
            if st=="":
                st="<MISSING>"
            states.append(s)
            cities.append(c)
            street.append(st)
            try:
                ph=re.findall(r'([0-9\)\( \-]+)',ps[2].text)
            except:
                ph = "<MISSING>"
            if ph ==[]:
                ph="<MISSING>"
            else:
                ph=ph[0].strip().replace("<","")
                if ph=="" or len(ph)<10:
                    ph="<MISSING>"

            tim=re.findall(r"Hours(.*pm|.*PM)",div.text,re.DOTALL)
            #print(len(tim))
            if tim==[]:
                tim="<MISSING>"
            else:
                tim=tim[0].replace("\r\n"," ").replace("\n"," ").strip()
                #print(tim)

            timing.append(tim)
            phones.append(ph)
            page_url.append(url)
            countries.append(count[urls.index(url)])

    print(len(locs),len(street))
    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("http://modoyoga.com/")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append(countries[i])
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append( page_url[i])  # page url
        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
