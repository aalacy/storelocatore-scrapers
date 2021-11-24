from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("ca_ecco_com")

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
    url = "https://ca.ecco.com/en/store-locator"
    stores_req = session.get(url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    scripts = soup.findAll("script")[14]
    scripts = str(scripts)
    scripts = scripts.replace("<script>", "")
    scripts = scripts.replace('var storesJson = [{"storeID":"', "")
    scripts = scripts.strip()
    locations = scripts.split('},{"storeID":"')
    for loc in locations:
        loc = loc + "}"
        store = loc.split('"isECCOStore":')[1].split("}")[0]
        if store == "true":
            storeid = loc.split('","name"')[0]
            storeid = storeid.lstrip(':"').strip()
            title = loc.split('"name":"')[1].split('","')[0].strip()
            title = title.replace("  ", " ")
            street = loc.split('"address1":"')[1].split('","')[0].strip()
            street = street.replace("  ", " ")
            address = loc.split('"address":"')[1].split('","')[0].strip()
            pcode = address.split(",")[-1].strip()
            city = loc.split('"city":"')[1].split('","')[0].strip()
            state = loc.split('"stateCode":"')[1].split('","')[0].strip()
            country = loc.split('"countryCode":"')[1].split('","')[0].strip()
            phone = loc.split('"phone":"')[1].split('","')[0].strip()
            phone = phone.lstrip("+")
            if phone == "":
                phone = "<MISSING>"
            lat = loc.split('"latitude":')[1].split(',"')[0]
            lng = loc.split('"longitude":')[1].split(',"')[0]
            if lat == "null":
                lat = "<MISSING>"
            if lng == "null":
                lng = "<MISSING>"
            hours = loc.split('"storeHours":')[1].split('],"')[0]
            hours = hours.lstrip('["')
            hours = hours.rstrip('"')
            soup = BeautifulSoup(hours, "html.parser")
            hours = soup.text
            hours = hours.replace("\\n", "").strip()
            hours = hours.replace("\\t\\t\\t", "-").strip()
            hours = hours.replace("\\t", "").strip()
            hours = hours.replace("--", " ").strip()

            data.append(
                [
                    "https://ca.ecco.com/",
                    "https://ca.ecco.com/en/store-locator",
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
