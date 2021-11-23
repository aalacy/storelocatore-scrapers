from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("rebag_com")

session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
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
    search_url = "https://www.rebag.com/store/"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    locations = soup.find("div", {"class": "store-content"}).findAll(
        "div", {"class": "store-details"}
    )
    for loc in locations:
        title = loc.find("h4", {"itemprop": "name"}).text.strip()
        street = loc.find("span", {"itemprop": "streetAddress"}).text.strip()
        city = loc.find("span", {"itemprop": "addressLocality"}).text.strip()
        state = loc.find("span", {"itemprop": "addressRegion"}).text.strip()
        pcode = loc.find("span", {"itemprop": "postalCode"}).text.strip()
        hours = loc.findAll("time", {"itemprop": "openingHours"})
        hoo = ""
        for hr in hours:
            hoo = hoo + " " + hr.text
        hoo = hoo.strip()
        data.append(
            [
                "https://www.rebag.com/",
                search_url,
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
                hoo,
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
