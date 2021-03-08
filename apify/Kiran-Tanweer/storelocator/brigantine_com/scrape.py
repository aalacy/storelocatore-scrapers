from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("brigantine_com")

session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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

        temp_list = []
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
    url = "http://www.brigantine.com/"
    stores_req = session.get(url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    locations = soup.find("div", {"class": "section-body grid clearfix"})
    loc_div = locations.findAll("div", {"class": "location"})
    for loc in loc_div:
        title = loc.find("h3", {"itemprop": "name"}).text
        phone = loc.find("p", {"class": "location-phone"}).text.strip()
        street = loc.find("span", {"itemprop": "streetAddress"}).text.strip()
        city = loc.find("span", {"itemprop": "addressLocality"}).text.strip()
        state = loc.find("span", {"itemprop": "addressRegion"}).text.strip()
        pcode = loc.find("span", {"itemprop": "postalCode"}).text.strip()
        pcode = pcode.rstrip("Click here to book a private event")
        pcode = pcode.rstrip("CLICK HERE TO BOOK A PRIVATE EVENT")
        hours = loc.find("div", {"class": "list-location"}).text
        hours = hours.replace("\n", " ").strip()

        data.append(
            [
                "http://www.brigantine.com/",
                "http://www.brigantine.com/",
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone,
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
