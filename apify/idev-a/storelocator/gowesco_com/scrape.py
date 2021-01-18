import csv
import json
from bs4 import BeautifulSoup as bs
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
    base_url = "https://www.gowesco.com/"
    res = session.get(
        "https://www.zip-codes.com/storelocator/serve-store.asp?p=1&apikey=QJ28AIT7TU4L4OQRQMRB&width=100%25&height=650&force_layout=horizontal-alt&zip=49445&city=Muskegon&state=MI&map_frame_col=FFFFFF&list_limit=10&store_col=5e91f6&result_col=333333&search=city&ref=https://www.gowesco.com/"
    )
    soup = bs(res.text, "lxml")
    page_links = soup.select("div.resPages a")
    links = [
        "https://www.zip-codes.com/storelocator/serve-store.asp?p=1&apikey=QJ28AIT7TU4L4OQRQMRB&width=100%25&height=650&force_layout=horizontal-alt&zip=49445&city=Muskegon&state=MI&map_frame_col=FFFFFF&list_limit=10&store_col=5e91f6&result_col=333333&search=city&ref=https://www.gowesco.com/"
    ]
    for x in page_links:
        links.append(x["href"])

    data = []
    for link in links:
        res = session.get(link)
        soup = bs(res.text, "lxml")
        geo_data = json.loads(res.text.split("var locations = ")[1].split(";")[0])
        store_list = soup.select("div.resLocation")
        for store in store_list:
            page_url = "https://www.gowesco.com/locations.html"
            address = store.select_one("input")["value"].split(", ")
            zip = address.pop()
            state = address.pop()
            city = address.pop()
            street_address = ", ".join(address)
            location_name = store.select_one("a.resName").text.split("\xa0").pop()
            country_code = "US"
            location_type = "<MISSING>"
            store_id = store.select_one("div.resNumber").string
            phone = (
                store.select_one("div.resLocationDetails div")
                .text.split("\r\n\t\t")[:-1]
                .pop()
                .replace("\u202d", "")[:-10]
                .replace("\u202c", "")
                .replace("Phone: ", "")
            )
            hours_of_operation = "<MISSING>"
            for geo_code in geo_data:
                if geo_code["id"] == store_id:
                    latitude = geo_code["lat"]
                    longitude = geo_code["lng"]
            store_number = "<MISSING>"

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
