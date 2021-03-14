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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://www.geocms.it/Server/servlet/S3JXServletCall?parameters=method_name%3DGetObject%26callback%3Dscube.geocms.GeoResponse.execute%26id%3D7%26query%3D%255BcountryCode%255D%2520%253D%2520%255B{}%255D%26clear%3Dtrue%26licenza%3Dgeo-todsgroupspa%26progetto%3DTods%26lang%3DALL&encoding=UTF-8"

    domain = "tods.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    countries = ["US", "PR", "GB"]
    for country in countries:
        response = session.get(start_url.format(country), headers=hdr)
        data = re.findall(r'GeoResponse.execute\((.+),"",7\)', response.text)[0]
        data = json.loads(json.loads(data))

        for poi in data["L"][0]["O"]:
            store_url = "https://www.tods.com/us-en/store-locator.html"
            location_name = poi["D"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["U"]["address"]
            street_address = (
                street_address.split("Plaza, ")[-1].split("hops, ")[-1].strip()
                if street_address
                else "<MISSING>"
            )
            city = poi["U"]["city"]
            city = city if city else "<MISSING>"
            state = poi["U"].get("region")
            state = state if state else "<MISSING>"
            zip_code = poi["U"]["zipCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["U"]["countryCode"]
            store_number = poi["U"]["branchCode"]
            phone = poi["U"].get("phone")
            phone = phone if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = poi["U"]["latitiude"]
            longitude = poi["U"]["longitude"]
            hoo = []
            days_dict = {
                "1": "Monday",
                "2": "tuesday",
                "3": "wednesday",
                "4": "thursday",
                "5": "friday",
                "6": "saturday",
                "7": "sunday",
            }
            hoo = []
            if poi["U"]["G"].get("hours"):
                for elem in poi["U"]["G"]["hours"]:
                    day = days_dict[elem["day"]]
                    if elem.get("From1"):
                        opens = elem["From1"]
                        closes = elem["To1"]
                        hoo.append(f"{day} {opens} - {closes}")
                    else:
                        hoo.append(f"{day} closed")
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
