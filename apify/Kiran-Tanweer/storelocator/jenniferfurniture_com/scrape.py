from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("jenniferfurniture_com")

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
    search_url = "https://cdn.shopify.com/s/files/1/1101/6302/t/179/assets/sca.storelocator_scripttag.js?v=1609906387&shop=jennifer-convertibles.myshopify.com"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    soup = str(soup)
    locations = soup.split('"locationsRaw":"')[1].split('}]"};')[0]
    locations = str(locations)
    location = locations.split('"lat')
    location.pop(0)
    for loc in location:
        loc = loc.lstrip('\\":\\"')
        lat = loc.split('\\"')[0]
        lng = loc.split('"lng\\":\\"')[1].split('\\"')[0]
        storeid = loc.split('\\"id\\":')[1].split(",\\")[0]
        title = loc.split('"name\\":\\"')[1].split('\\",')[0]
        phone = loc.split('"phone\\":\\"')[1].split('\\"')[0]
        link = loc.split('"web\\":\\"')[1].split('",\\')[0]
        hours = loc.split('"schedule\\":\\"')[1].split('",\\')[0]
        street = loc.split('"address\\":\\"')[1].split('\\"')[0].split()
        city = loc.split('"city\\":\\"')[1].split('\\"')[0]
        state = loc.split('"state\\":\\"')[1].split('\\"')[0]
        pcode = loc.split('"postal\\":\\"')[1].split('\\"')[0]
        country = loc.split('"country\\":\\"')[1].split('\\"')[0]
        link = link.replace("\\\\\\", "").strip()
        hours = hours.replace("\\\\r<br/>", "").strip()
        hours = hours.replace("\\", "").strip()
        hours = hours.replace("PM", "PM.").strip()
        hours = hours.replace("PM.", "PM. ").strip()
        hours = hours.replace("  ", " ").strip()
        hours = hours.replace(". .", ". ").strip()
        hours = hours.replace("  ", " ").strip()
        street.pop(0)
        street.pop(0)
        street.pop(0)
        street.pop(0)
        street = " ".join([str(elem) for elem in street])
        street = street.lstrip("Place, ")

        data.append(
            [
                "https://www.jenniferfurniture.com/",
                link,
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
