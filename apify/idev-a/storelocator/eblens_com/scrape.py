import csv
import json
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list

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
    base_url = "https://www.eblens.com"
    zip_codes = static_zipcode_list(radius=50, country_code=SearchableCountries.USA)
    data = []
    store_ids = []
    for zip_code in zip_codes:
        payload = {"locationSearch": zip_code, "maxrows": 20}
        res = session.post(
            "https://www.eblens.com/functions/storelocator.cfc?method=generateStoreLocatorResultsAJAX&random=25",
            data=payload,
        )
        if "No Stores Found" in res.text:
            continue
        content = json.loads(res.text)["STOREDISP"]
        soup = bs(content, "lxml")
        store_list = soup.select("div.mapAddress")
        for store in store_list:
            page_url = store.select_one("span.store_detail a")["href"]
            location_name = store.select_one("a.store_name").contents[0].string
            if "Closed" in store.select_one("a.store_name").text:
                location_name += " Closed"
            address_content = store.select_one("span.store_addr").contents
            address = []
            for x in address_content:
                if x.string is not None and x.string != "\n":
                    address.append(x.string)
            phone = address.pop()
            address_detail = address.pop()
            city = address_detail.split(", ")[0]
            state = address_detail.split(", ")[1].split(" ")[0]
            zip = address_detail.split(", ")[1].split(" ")[1]
            street_address = " ".join(address).strip()
            store_id = location_name + street_address
            if store_id in store_ids:
                continue
            store_ids.append(store_id)
            country_code = "US"
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            geo = (
                store.select_one("span.store_directions a")["href"]
                .split("sll=")[1]
                .split("&")[0]
            )
            latitude = geo.split(",")[0]
            longitude = geo.split(",")[1]
            res1 = session.get(page_url)
            detail = bs(res1.text, "lxml")
            hours_of_operation = detail.select_one("ul.storeHours").text

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
                    '="' + phone + '"',
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
