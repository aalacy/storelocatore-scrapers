import csv
import re
from bs4 import BeautifulSoup
import requests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('stopandgostores_com')



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
    urls=[]

    res=requests.get("https://www.stopandgostores.com/locations")
    soup = BeautifulSoup(res.text, 'html.parser')
    div = soup.find('div', {'id': 'comp-im6g8lb3_NewsPostsView_i6m78132490_dup_i6qm3pea337_dup_i6tbtsmw87_dup_i70h8xsg189_dup_i7g5p5vd171_im6g8lb9_Array__0_0_i7g5p5ve'})
    tex=div.text.replace("\n","").replace("\xa0","").replace("stopandgostores.comStore Profile","").split("S&G")
    strongs=soup.find_all('strong')
    del strongs[0]
    for strong in strongs:
        locs.append(strong.text.strip())

    del tex[0]
    #logger.info(tex)
    for t in tex:
        t=t.replace("xxx-xxxx","").replace("xxx-xxx-xxxx","").replace("xxx-","")
        id=re.findall(r'Phone([\d]+)@',t)
        if id==[]:
            id = re.findall(r'Fax([\d]+)@', t)
            if id==[]:
                id = re.findall('Liquor Orders([\d]+)@',t)
                if id ==[]:
                    id="<MISSING>"
                else:
                    id=id[0]
            else:
                id=id[0]
        else:
            id=id[0]

        ids.append(id)
        te=t.split("Phone")[0]
        te=re.sub("#"+id,"",te).strip()
        #logger.info(te)
        num=re.findall(r'[0-9\-]+',te)[-1]
        if num == "-":
            num=re.findall(r'[0-9\-]+',te)[-2]
        if len(num)==18:
            zips.append(num[:6])
            if len(num[6:]) < 10:
                phones.append("<MISSING>")
            else:
                phones.append(num[6:])
        else:
            zips.append(num[:5])
            if len(num[5:])<10:
                phones.append("<MISSING>")
            else:
                phones.append(num[5:])
        te=te.replace(num,"").strip()
        c=re.findall('[A-Z][^A-Z]*',te.split(" ")[-2])[-1]
        s=te.split(" ")[-1]
        states.append(s.strip())
        cities.append(c.replace(",","").strip())
        #logger.info(te)
        street.append(re.sub(r"(\w)([A-Z][a-z]+)", r"\1 \2",te.replace(c,"").replace(s,"")).strip().strip(","))

        #break
    logger.info(len(tex))
    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.stopandgostores.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append('US')
        row.append(ids[i])  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append("<MISSING>")  # lat
        row.append("<MISSING>")  # long
        row.append("<MISSING>")  # timing
        row.append("https://www.stopandgostores.com/locations")  # page url
        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
