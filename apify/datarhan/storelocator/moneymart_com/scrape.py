import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests

DOMAIN = "moneymart.com"


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
    # Your scraper here
    session = SgRequests()

    items = []
    gathered_items = []

    hdr = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Host": "www.moneymart.com",
        "Origin": "https://moneymart.com",
        "Referer": "https://moneymart.com/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
    }

    body = '{"lat":40.75368539999999,"lng":-73.9991637,"startRcdNum":"0","radius":"10000","StoreNum":"","searchText":"  10001   "}'

    all_response = session.post(
        "https://www.moneymart.com/StoreDetails/GoogleAPIServiceCall",
        data=body,
        headers=hdr,
    )
    soup = BeautifulSoup(all_response.content, "html.parser")
    all_stores = soup.find_all("store")

    for store_data in all_stores:
        location_name = store_data.businessname.text
        street_address = store_data.address1.text
        if store_data.address2:
            street_address += " " + store_data.address2.text
        street_address = street_address if street_address else "<MISSING>"
        city = store_data.city
        city = city.text if city else "<MISSING>"
        print(store_data)
        state = store_data.state
        state = state.text if state else "<MISSING>"
        zip_code = store_data.postalcode.text
        if zip_code:
            if len(zip_code) > 5:
                zip_code = "{}-{}".format(zip_code[:5], zip_code[5:])
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = store_data.country.text
        country_code = country_code if country_code else "<MISSING>"
        store_number = store_data.storenum.text
        phone = store_data.phone.text
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = store_data.latitude.text
        latitude = latitude if latitude else "<MISSING>"
        longitude = store_data.longitude.text
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = store_data.storehours.text
        hours_of_operation = hours_of_operation if hours_of_operation else "<MISSING>"
        store_url = (
            "https://www.moneymart.com/StoreDetails/StoreDetails?US/{}/{}/{}/{}-/{}"
        )
        store_url = store_url.format(
            state,
            city.replace(" ", "-"),
            street_address.replace(" ", "-"),
            zip_code,
            store_number,
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

        check = location_name.strip().lower() + " " + street_address.strip().lower()
        if check not in gathered_items:
            gathered_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
