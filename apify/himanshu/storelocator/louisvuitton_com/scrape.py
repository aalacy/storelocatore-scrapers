import csv

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

    start_url = "https://us.louisvuitton.com/ajax/getStoreJson.jsp?storeLang=eng-us&cache=NoStore&pageType=storelocator_section&flagShip=false&latitudeCenter=79.07551387583152&longitudeCenter=-65.4902108522589&latitudeA=89.91911250263446&longitudeA=-180&latitudeB=-81.17149408339752&longitudeB=180&doClosestSearch=false&zoomLevel=0&country=&categories=&clickAndCollect=false&productId=&countryId=&osa=null&Ntt=10001"
    domain = "louisvuitton.com"

    hdr = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": "https://us.louisvuitton.com/eng-us/stores",
        "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    data = session.get(start_url, headers=hdr).json()
    all_locations = data["stores"]

    for poi in all_locations:
        store_url = poi["url"]
        location_name = poi["name"].replace("&#039;", "'")
        street_address = poi["street"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["storeId"]
        phone = (
            poi["phone"].replace("(Client Services)", "").replace("(Kundenservice)", "")
        )
        phone = phone.strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hoo = []
        for e in poi["openingHours"]:
            day = e["openingDay"]
            hours = e["openingHour"]
            hoo.append(f"{day} {hours}")
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
        if (
            hours_of_operation
            == "Monday Tuesday Wednesday Thursday Friday Saturday Sunday"
        ):
            hours_of_operation = "<MISSING>"

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
