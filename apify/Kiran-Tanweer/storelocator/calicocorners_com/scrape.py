from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("calicocorners_com")

session = SgRequests()
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
}

def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        temp_list = []  # ignoring duplicates
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)
        logger.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    data = []
    store = []
    store_id =[]
    title = []
    adr = []
    hours = []
    Phone = []
    i=0
    url = 'https://www.calicocorners.com/storelocator.aspx'
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    locs = soup.find("div", {"id": "ctl00_PageContent_pnlStores"})
    info = locs.findAll("div", {"class": "storehours pad-no"})
    info2 = locs.findAll("div", {"class": "storehours storehr-popup"})
    info3 = locs.findAll("div", {"class": "calicoalinkdiv"})
    for i in range(len(info)):
        if i%2 == 0:
            tit = info[i].text.strip()
            title.append(tit)
        else:
            address = info[i].text
            ph = address.split('Phone:')[1].split('Email:')[0].strip()
            Phone.append(ph)

    for i in info2:
        hour = i.text
        hour = hour.replace("  ", " ")
        hour = hour.replace("Closed", "Closed ")
        hour = hour.replace("PM", "PM ").strip()
        hours.append(hour)

    for i in range(len(info3)): 
        if (i % 3 == 0):
            locator = info3[i].find('a')['onclick'] #address
            locator = locator.split('trackgetdirections(')[1].split(')')[0]
            locator = locator.replace("'", "").strip()
            adr.append(locator)
        else:
            locator = info3[i].find('a')['onclick'].strip() #storeid and city
            store.append(locator)
    for i in range(len(store)): # separating store_id from city
        if (i % 2 == 0):
            storeid = store[i].split("trackOutboundLink('storepage.aspx?storeid=")[1].split(" '")[0].strip()
            store_id.append(storeid)

    for i,j,k,l,m in zip(adr, hours, title, Phone, store_id):
        title = k
        storeid = m
        address = i
        address = address.split(',')
        street = address[0].strip()
        city = address[1].strip()
        state = address[2].strip()
        pcode = address[3].strip()
        phone = l
        HOO = j

        if street == 'Strawberry Village Shopping Center Suite 121':
            street = '800 Redwood Highway Frontage Road, Strawberry Village Shopping Center Suite 121'

        if street == 'Suite 184':
            street = '2355 Vanderbilt Beach Rd, Suite 184'

        if street == 'ParkTowne Village':
            street = '1630 E. Woodlawn Road, ParkTowne Village'

        if street == 'Suite 126/128':
            street = '1860 Laskin Road, Suite 126/128'
            
    
        data.append(
            [
                "https://www.calicocorners.com/",
                "https://www.calicocorners.com/storelocator.aspx",
                title,
                street,
                city,
                state,
                pcode,
                "US",
                storeid,
                phone,
                "Design Shops",
                "<INACCESSIBLE>",
                "<INACCESSIBLE>",
                HOO,
            ]
        )
    return data

        
def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
