import csv
from lxml import html
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
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

        for row in data:
            writer.writerow(row)


def fetch_data():
    out = []

    locator_domain = "https://www.garageclothing.com/"
    api_url = "https://www.garageclothing.com/on/demandware.store/Sites-DynamiteGarageCA-Site/en_CA/Stores-FindStores?showMap=true&radius=100000 Km&postalCode=L5M4Z5"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js["stores"]:
        page_url = "<MISSING>"
        location_name = j.get("name")
        location_type = j.get("brand")
        street_address = f"{j.get('address1')} {j.get('address2') or ''}".strip()
        phone = j.get("phone")
        state = j.get("stateCode")
        postal = j.get("postalCode")
        country_code = j.get("countryCode")
        if country_code == "CA":
            page_url = "https://www.garageclothing.com/ca/stores?showMap=true"
        if country_code == "US":
            page_url = "https://www.garageclothing.com/us/stores?showMap=true"
        city = j.get("city")
        store_number = j.get("ID")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours_of_operation = (
            "".join(j.get("storeHours")).replace("\n\n", "").replace("\n", "").strip()
            or "<MISSING>"
        )
        if hours_of_operation != "<MISSING>":
            hours_of_operation = html.fromstring(hours_of_operation)
            hours_of_operation = hours_of_operation.xpath("//*//text()")
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = " ".join(hours_of_operation)
        if hours_of_operation.count("CLOSED - CLOSED") == 7:
            hours_of_operation = "Closed"
        hours_of_operation = hours_of_operation.replace("CLOSED - CLOSED", "Closed")

        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        out.append(row)

    locator_domain = "https://www.garageclothing.com/"
    api_url = "https://www.garageclothing.com/on/demandware.store/Sites-DynamiteGarageUS-Site/en_US/Stores-FindStores?showMap=true&radius=100000 Km&postalCode=92618"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js["stores"]:
        page_url = "<MISSING>"
        location_name = j.get("name")
        location_type = j.get("brand")
        street_address = f"{j.get('address1')} {j.get('address2') or ''}".strip()
        phone = j.get("phone")
        state = j.get("stateCode")
        postal = j.get("postalCode")
        country_code = "".join(j.get("countryCode"))
        if country_code == "CA":
            page_url = "https://www.garageclothing.com/ca/stores?showMap=true"
        if country_code == "US":
            page_url = "https://www.garageclothing.com/us/stores?showMap=true"
        city = j.get("city")
        store_number = j.get("ID")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours_of_operation = (
            "".join(j.get("storeHours")).replace("\n\n", "").replace("\n", "").strip()
            or "<MISSING>"
        )
        if hours_of_operation != "<MISSING>":
            hours_of_operation = html.fromstring(hours_of_operation)
            hours_of_operation = hours_of_operation.xpath("//*//text()")
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = " ".join(hours_of_operation)
        if hours_of_operation.count("CLOSED - CLOSED") == 7:
            hours_of_operation = "Closed"
        hours_of_operation = hours_of_operation.replace("CLOSED - CLOSED", "Closed")

        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
