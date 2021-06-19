import re
import csv
import pycountry

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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://us.maxmara.com/store-locator?listJson=true&withoutRadius=false&country={}"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": "https://us.maxmara.com/store-locator",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
        "x-newrelic-id": "UAYAWFVXGwICXVhaAwUE",
        "x-requested-with": "XMLHttpRequest",
    }
    for e in pycountry.countries:
        data = session.get(start_url.format(e.alpha_2), headers=hdr).json()
        all_locations = data["features"]
        for poi in all_locations:
            store_url = f"https://us.maxmara.com/store/{poi['properties']['name']}"
            location_name = poi["properties"]["displayName"]
            street_address = (
                poi["properties"]["formattedAddress"].split(",")[0].split("Outlet")[-1]
            )
            if street_address == ".. ..":
                street_address = "<MISSING>"
            city = poi["properties"]["city"]
            state = poi["properties"]["prov"].split("-")[-1]
            state = state if state else "<MISSING>"
            zip_code = poi["properties"]["zip"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["properties"]["country"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["properties"]["name"]
            phone = poi["properties"]["phone1"]
            phone = phone if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = poi["properties"]["lat"]
            longitude = poi["properties"]["lng"]
            hoo = []
            for day, hours in poi["properties"]["openingHours"].items():
                hoo.append(f"{day} {hours[0]}")
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

            item = [
                domain,
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
