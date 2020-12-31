import csv
import re

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

    base_link = "https://qualitymartnc.com/wp-json/wpgmza/v1/markers/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxR0gEJFGeUgsSKgYLRsbVKtQCV7hBN"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    store_data = session.get(base_link, headers=headers).json()

    data = []
    locator_domain = "qualitymartnc.com"

    for store in store_data:
        location_name = store["title"].upper()

        raw_address = store["address"].replace("N Advance", "N, Advance").split(",")
        if "USA" in raw_address[-1].upper():
            raw_address.pop(-1)

        street_address = raw_address[0].strip()
        city = raw_address[1].strip()
        state = raw_address[-1].strip()[:-6].strip()
        zip_code = raw_address[-1][-6:].strip()

        if "NC" in zip_code:
            state = "NC"
            zip_code = "<MISSING>"
        if not state:
            state = raw_address[2].strip()

        country_code = "US"
        store_number = location_name.split("#")[1]

        raw_types = store["description"]
        location_type = (
            raw_types[raw_types.rfind("strong>") + 7 : raw_types.rfind("</p>")]
            .replace("<br />", ",")
            .replace(",,", "")
        )
        if location_type[:1] == ",":
            location_type = location_type[1:]
        if not location_type:
            location_type = "<MISSING>"
        try:
            phone = re.findall(r"[(\d)]{5} [\d]{3}-[\d]{4}", store["description"])[0]
        except:
            phone = "<MISSING>"

        hours_of_operation = store["description"].split("<br />")[2]
        if "Hours:" in hours_of_operation:
            hours_of_operation = (
                hours_of_operation.replace("Hours:", "").strip() + " daily"
            )
        latitude = store["lat"]
        longitude = store["lng"]

        if float(latitude) == 0:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        data.append(
            [
                locator_domain,
                "https://qualitymartnc.com/locations/",
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
