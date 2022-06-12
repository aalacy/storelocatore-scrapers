import csv
import json
from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
    base_url = "https://www.mandee.com/"
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Length": "0",
        "Host": "storelocator.w3apps.co",
        "Origin": "https://storelocator.w3apps.co",
        "Referer": "https://storelocator.w3apps.co/map.aspx?shop=mandee-online&container=false",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    res = session.post(
        "https://storelocator.w3apps.co/get_stores2.aspx?shop=mandee-online&all=1",
        headers=headers,
    )
    store_list = json.loads(res.text)["location"]
    data = []

    for store in store_list:
        store_number = store["id"]
        city = store["city"]
        state = store["state"]
        page_url = "<MISSING>"
        hours_of_operation = "<MISSING>"
        location_name = store["name"]
        street_address = (
            store["address"]
            if store["address2"] == ""
            else store["address"] + ", " + store["address2"]
        )
        zip = store["zip"]
        country_code = "<MISSING>" if store["country"] == "" else store["country"]
        phone = "<MISSING>" if store["phone"] == "" else store["phone"]
        location_type = "<MISSING>"
        latitude = store["lat"]
        longitude = store["long"]

        data.append(
            [
                base_url,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zip,
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


if __name__ == "__main__":
    scrape()
