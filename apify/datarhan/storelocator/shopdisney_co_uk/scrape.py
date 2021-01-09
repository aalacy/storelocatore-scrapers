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

    DOMAIN = "shopdisney.co.uk"
    start_url = "https://locations.shopdisney.co.uk/rest/locatorsearch?lang=en_US"
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    body = '{"request":{"appkey":"D5871172-8772-11E2-9B36-44EFA858831C","formdata":{"geoip":"start","dataview":"store_default","limit":500,"geolocs":{"geoloc":[{"addressline":"","country":"UK","latitude":"","longitude":""}]},"searchradius":"5000","radiusuom":"km","where":{"and":{"storetype":{"eq":""}}}},"geoip":""}}'
    response = session.post(start_url, data=body, headers=headers)
    data = json.loads(response.text)

    for poi in data["response"]["collection"]:
        if poi["country"] != "UK":
            continue
        store_url = "<MISSING>"
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address1"]
        if poi["address2"]:
            street_address += ", " + poi["address2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["postalcode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["clientkey"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hoo_dict = {}
        for day, hours in poi.items():
            if "_op" in day:
                day = day.split("_")[0]
                opens = hours
                if hoo_dict.get(day):
                    hoo_dict[day]["opens"] = opens
                else:
                    hoo_dict[day] = {}
                    hoo_dict[day]["opens"] = opens
            if "_cl" in day:
                day = day.split("_")[0]
                closes = hours
                if hoo_dict.get(day):
                    hoo_dict[day]["closes"] = closes
                else:
                    hoo_dict[day] = {}
                    hoo_dict[day]["closes"] = closes
        hoo = []
        for day, hours in hoo_dict.items():
            if hours["opens"] == "Closed":
                hoo.append(f"{day} Closed")
            else:
                opens = hours["opens"]
                closes = hours["closes"]
                hoo.append(f"{day} {opens} - {closes}")
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        store_url = "https://stores.shopdisney.co.uk/{}/{}/{}/?utm_source=Disney+Store&utm_medium=Website&utm_campaign=Store+Locator"
        store_url = store_url.format(
            poi["analytics_city"], poi["analytics_store_name"], poi["clientkey"]
        )

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
