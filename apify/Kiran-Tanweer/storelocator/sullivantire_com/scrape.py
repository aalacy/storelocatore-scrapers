from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("sullivantire_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
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

    url = "https://www.sullivantire.com/locations?resultsPerPage=500&page=1&zipCode="
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.findAll("div", {"class": "media-location--item"})
    for loc in loclist:
        link = loc.find(
            "a",
            {
                "class": "button button--extra-small button--clear-green button--store-info"
            },
        )["href"]
        link = "https://www.sullivantire.com" + link
        title = loc.find("h4", {"class": "big location-name"}).text
        address = loc.find("div", {"class": "detail"}).text.strip()

        address_parts = [
            item.strip()
            for item in address.replace("\r", "").split("\n")
            if item.strip() != ""
        ]

        street = address_parts[0]
        city = address_parts[1].split(", ")[0]
        state = address_parts[1].split(", ")[1].split(" ")[0]
        pcode = address_parts[1].split(", ")[1].split(" ")[1]

        phone = loc.find("a", {"class": "text-green--bright-medium"}).text
        script = loc.find("script")
        script = str(script)
        coords = script.split('"GeoCoordinates",')[1].split("}")[0]
        lat = coords.split('"latitude":"')[1].split('","')[0]
        lng = coords.split('"longitude":"')[1].split('"')[0]
        hours = script.split('"openingHours":')[1].split(',"contactPoint"')[0]
        hours = hours.lstrip('"')
        hours = hours.rstrip('"')
        hours = hours.replace("PMSa", "PM Sat")

        data.append(
            [
                "https://www.sullivantire.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
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
