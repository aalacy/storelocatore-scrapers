from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("us_ecco_com")

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
    dedup = []
    url = "https://us.ecco.com/store-locator"
    stores_req = session.get(url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    scripts = soup.findAll("script")[12]
    scripts = str(scripts)
    locations = scripts.split('},{"storeID"')
    for loc in locations:
        loc = loc + "}"
        store = loc.split('"isECCOStore":')[1].split("}")[0]
        if store == "true":
            storeid = loc.split('","name"')[0]
            storeid = storeid.lstrip(':"').strip()
            title = loc.split('"name":"')[1].split('","')[0].strip()
            street = loc.split('"address1":"')[1].split('","')[0].strip()
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
            hours = hours.split("},{")
            hoo = ""
            for hr in hours:
                day = hr.split('"label":"')[1].split('","')[0]
                hour = hr.split('"data":"')[1].split('"')[0]
                h1 = day + " " + hour
                hoo = h1 + " " + hoo
            data_dedup = street + "-" + city + "-" + state + "-" + pcode
            if data_dedup not in dedup:
                dedup.append(data_dedup)

                data.append(
                    [
                        "https://us.ecco.com/",
                        "https://us.ecco.com/store-locator",
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
