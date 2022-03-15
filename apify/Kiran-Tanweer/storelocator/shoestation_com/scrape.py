from bs4 import BeautifulSoup
import csv
import re
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("shoestation_com")

session = SgRequests()

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "_evga_00e0=e50c01663d2833fd.; mage-cache-storage=%7B%7D; mage-cache-storage-section-invalidation=%7B%7D; form_key=3TfoRi9kC4Rz3M9B; mage-messages=; recently_viewed_product=%7B%7D; recently_viewed_product_previous=%7B%7D; recently_compared_product=%7B%7D; recently_compared_product_previous=%7B%7D; product_data_storage=%7B%7D; _ga=GA1.2.548867291.1612637819; _gid=GA1.2.1337555984.1612637819; _fbp=fb.1.1612637823822.1887997027; rl_visitor_history=7d3135d8-1c01-4c3e-85b8-1a7674564364; sifi_user_id=undefined; _sp_ses.4e8d=*; PHPSESSID=350caaae6ec7be916e9e812c4c2afe06; form_key=3TfoRi9kC4Rz3M9B; _uetsid=1694ecd068ad11ebaca2b9d780c52a14; _uetvid=169532c068ad11eb94caabf623757d75; mage-cache-sessid=true; sc_fb_session={%22start%22:1612637818987%2C%22p%22:4}; _sp_id.4e8d=f76282c2f90e09ab.1612637820.3.1612670625.1612667125; sc_fb={%22v%22:0.3%2C%22t%22:614%2C%22p%22:4%2C%22s%22:1%2C%22b%22:[]%2C%22pv%22:[]%2C%22tr%22:0%2C%22e%22:[]}",
    "Host": "www.shoestation.com",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    url = "https://www.shoestation.com/storelocator/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    info = soup.findAll("div", {"class": "amlocator-store-desc"})
    for loc in info:
        hours = loc.find("div", {"class": "amlocator-schedule-table"}).text
        hours = re.sub(pattern, " ", hours)
        hours = re.sub(cleanr, " ", hours)
        hours = hours.replace("\n", " ")
        hours = hours.strip()
        title = loc.find("div", {"class": "amlocator-title"}).text
        address = loc.find("div", {"class": "amlocator-store-information"}).text
        address = re.sub(pattern, " ", address)
        address = re.sub(cleanr, " ", address)
        city = address.split("City:")[1].split("Zip:")[0].strip()
        street = address.split("Address:")[1].split("Distance:")[0].strip()
        state = address.split("State:")[1].split("Address:")[0].strip()
        pcode = address.split("Zip:")[1].split("State:")[0].strip()

        data.append(
            [
                "https://www.shoestation.com/storelocator/",
                "https://www.alaskacommercial.com/store-locator",
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                hours,
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
