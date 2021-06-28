import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import SgLogSetup
import time
from sgscrape import sgpostal as parser

logger = SgLogSetup().get_logger("elietahari_com")

session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
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
    search_url = "https://cdn.shopify.com/s/files/1/0350/8997/3385/t/49/assets/ndnapps-geojson.js?v=12382587392219603945"
    stores_req = session.get(search_url, headers=headers)
    soup = stores_req.text
    r_text = soup.split("eqfeed_callback(")[1].split(")")[0]
    locations = r_text.split("}},")
    link = "https://www.elietahari.com/pages/store-locator"
    r = session.get(link, headers=headers)
    bs = BeautifulSoup(r.text, "html.parser")
    hours = bs.findAll("div", {"class": "hours"})
    for locs, hr in zip(locations, hours):
        hoo = hr.text
        hoo = hoo.replace("\n", " ")
        hoo = hoo.replace("Opens", "")
        hoo = hoo.replace("Hours", "")
        hoo = hoo.replace("  ", " ")
        hoo = hoo.strip()
        title = locs.split('name":"')[1].split('",')[0]
        address = locs.split('"address":"')[1].split('",')[0]
        phone = locs.split('phone":')[1].split(",")[0]
        phone = phone.strip('"')
        if phone == "null":
            phone = "<MISSING>"
        storeid = locs.split('"id":')[1].split(',"')[0]
        url = "https://www.elietahari.com" + locs.split('url":"')[1].split('",')[0]
        url = url.replace("\\", "")
        lat = locs.split('"lat":"')[1].split('",')[0]
        lng = locs.split('"lng":"')[1].split('",')[0]
        address = address.rstrip(", United States")
        parsed = parser.parse_address_intl(address)
        street1 = parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
        street = (
            (street1 + ", " + parsed.street_address_2)
            if parsed.street_address_2
            else street1
        )
        city = parsed.city if parsed.city else "<MISSING>"
        state = parsed.state if parsed.state else "<MISSING>"
        pcode = parsed.postcode if parsed.postcode else "<MISSING>"
        country = "US"

        data.append(
            [
                "https://www.elietahari.com/",
                url,
                title,
                street,
                city,
                state,
                pcode,
                country,
                storeid,
                phone,
                "<MISSING>",
                lat,
                lng,
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
