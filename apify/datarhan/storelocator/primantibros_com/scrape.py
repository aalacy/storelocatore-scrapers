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

    DOMAIN = "primantibros.com"
    start_url = (
        "https://hosted.where2getit.com/primantibros/rest/locatorsearch?lang=en_US"
    )

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    body = '{"request":{"appkey":"7CDBB1A2-4AC6-11EB-932C-8917919C4603","formdata":{"geoip":false,"dataview":"store_default","limit":200,"google_autocomplete":"true","geolocs":{"geoloc":[{"addressline":"17011","country":"","latitude":"","longitude":""}]},"searchradius":"500","where":{"or":{"retail":{"eq":""},"outlet":{"eq":""},"factory":{"eq":""},"promo":{"eq":""}}},"false":"0"}}}'
    response = session.post(start_url, data=body, headers=headers)
    data = json.loads(response.text)

    for poi in data["response"]["collection"]:
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address1"]
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["postalcode"]
        country_code = poi["country"]
        store_number = poi["clientkey"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hoo = []
        for k, v in poi.items():
            if "hours" in k:
                day = k.replace("hours", "")
                hoo.append(f"{day} {v}")
        hours_of_operation = (
            " ".join(hoo).replace("holiday None", "") if hoo else "<MISSING>"
        )
        store_url = f'https://locations.primantibros.com/{state}/{city.replace(" ", "-")}/{store_number}/'

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
