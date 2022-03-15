import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
        for row in data:
            writer.writerow(row)


def fetch_data():

    base_link = "https://maps.stores.staples.ca/api/getAsyncLocations?template=search&level=search&search=&lat=62.454674&lng=-114.405169&radius=5000"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    raw_data = session.get(base_link, headers=headers).json()["maplist"]

    item = BeautifulSoup(raw_data, "lxml")
    stores = (
        str(item.contents[0])
        .split('list">')[1]
        .split(",</div>")[0]
        .replace("\r\n", "")
        .split(",{   ")
    )

    data = []
    for i in stores:
        if i[0] != "{":
            i = "{" + i
        i = i.replace('"{\\', "{\\").replace("\\", "").split(',"children')[0] + "}}"
        store = json.loads(i)

        locator_domain = "staples.ca"
        location_name = store["location_name"] + " " + store["fid"]
        street_address = (
            (store["address_1"] + " " + store["address_2"])
            .replace("u00e9", "e")
            .replace("u00e7", "c")
            .replace("u00f4", "o")
            .strip()
        )
        city = store["city"]
        state = store["region"]
        zip_code = store["post_code"]
        country_code = store["country"]
        store_number = store["fid"].replace("CA-", "").strip()
        location_type = "<MISSING>"
        phone = store["local_phone"]

        hours_of_operation = ""
        raw_hours = store["hours_sets:primary"]["days"]
        for day in raw_hours:
            if raw_hours[day] == "closed":
                clean_hours = day + " closed"
            else:
                opens = raw_hours[day][0]["open"]
                closes = raw_hours[day][0]["close"]
                clean_hours = day + " " + opens + "-" + closes
            hours_of_operation = (hours_of_operation + " " + clean_hours).strip()

        latitude = store["lat"]
        longitude = store["lng"]
        link = store["url"]

        data.append(
            [
                locator_domain,
                link,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
