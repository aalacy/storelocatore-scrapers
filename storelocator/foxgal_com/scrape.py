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
    base_url = "https://www.foxgal.com/"
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "cookie": "_gcl_au=1.1.52585336.1610790288; _ga=GA1.2.222042547.1610790288; _gid=GA1.2.781937750.1610790288; PHPSESSID=47382a3126f0046e58b8e56d68cb8d02; _fbp=fb.1.1610790300650.1322115322; _gat=1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    res = session.get(
        "https://www.foxgal.com/wp-admin/admin-ajax.php?action=store_search&lat=32.77666&lng=-96.79699&max_results=10&search_radius=25&autoload=1",
        headers=headers,
    )
    store_list = json.loads(res.text)
    data = []

    for store in store_list:
        store_number = store["id"]
        city = store["city"]
        state = store["state"]
        page_url = store["url"]
        soup = bs(store["hours"], "lxml")
        hours_of_operation = soup.text.replace("\n", " ").replace("–", "-")
        location_name = store["store"].replace("&#038;", "&")
        street_address = store["address"]
        zip = store["zip"]
        country_code = store["country"]
        phone = store["phone"]
        location_type = "<MISSING>"
        latitude = store["lat"]
        longitude = store["lng"]

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
