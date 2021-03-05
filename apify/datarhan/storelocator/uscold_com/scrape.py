import re
import csv
import json

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
    # Your scraper here
    session = SgRequests()

    items = []

    DOMAIN = "uscold.com"
    start_url = "https://www.uscold.com/wp-json/wpgmza/v1/datatables/"

    response = session.get("https://www.uscold.com/facilitiesmap/")
    re.findall('restnonce":"(.+?)",', response.text)

    body = "columns%5B0%5D%5Bdata%5D=0&columns%5B0%5D%5Bname%5D=&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=true&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=1&columns%5B1%5D%5Bname%5D=&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=2&columns%5B2%5D%5Bname%5D=&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=3&columns%5B3%5D%5Bname%5D=&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=4&columns%5B4%5D%5Bname%5D=&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=5&columns%5B5%5D%5Bname%5D=&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B6%5D%5Bdata%5D=6&columns%5B6%5D%5Bname%5D=&columns%5B6%5D%5Bsearchable%5D=true&columns%5B6%5D%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=1&order%5B0%5D%5Bdir%5D=asc&start=0&length=-1&search%5Bvalue%5D=&search%5Bregex%5D=false&phpClass=WPGMZA%5CMarkerListing%5CAdvancedTable&map_id=1"
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "www.uscold.com",
        "Origin": "https://www.uscold.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "X-DataTables-Draw": "2",
        "X-Requested-With": "XMLHttpRequest",
        "X-WP-Nonce": re.findall('restnonce":"(.+?)",', response.text)[0],
        "X-WPGMZA-Action-Nonce": re.findall('datatables":"(.+?)",', response.text)[0],
    }
    response = session.post(start_url, data=body, headers=headers)
    data = json.loads(response.text)

    for poi in data["data"]:
        store_url = "<MISSING>"
        location_name = poi[1]
        address_raw = poi[3]
        if len(address_raw.split(", ")) == 4:
            if "USA" in address_raw.split(", ")[-1]:
                address_raw = ", ".join(address_raw.split(", ")[:-1])
            else:
                address_raw = [
                    " ".join(address_raw.split(", ")[:2])
                ] + address_raw.split(", ")[2:]
                address_raw = ", ".join(address_raw)
        if len(address_raw.split(", ")) == 2:
            address_raw = ", ".join(
                [
                    address_raw.split(", ")[0],
                    location_name.lower().capitalize(),
                    address_raw.split(", ")[-1],
                ]
            )
        city = address_raw.split(", ")[1]
        if len(city.split()[-1]) == 1:
            city = " ".join(city.split()[:-1])
        if city == "Mcdonough":
            city = "McDonough"
        if city == "Lake city":
            city = "Lake City"
        street_address = address_raw.split(", ")[0].replace(city, "")
        state = address_raw.split(", ")[-1].split()[0]
        zip_code = address_raw.split(", ")[-1].split()[-1].strip()
        if len(zip_code) == 2:
            zip_code = "<MISSING>"
        if "Ste" in city:
            street_address = ", ".join(address_raw.split(", ")[:-1])
            city = street_address.split()[-1]
            street_address = street_address.replace(city, "")
        if "Building" in city:
            street_address += " " + city
            city = "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        if "tel:" in poi[4].lower():
            phone = poi[4].lower().split("tel:")[1].split("<br")[0].strip()
        else:
            phone = poi[4].lower().split("p:")[1].split("<br")[0].strip()
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"

        item = [
            DOMAIN,
            store_url,
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
