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
    base_url = "https://www.petesfresh.com"
    res = session.get("https://www.petesfresh.com/stores")
    store_list = json.loads(
        res.text.split("jQuery.extend(Drupal.settings, ")[1].split("</script>")[0][:-14]
    )["gmap"]["auto1map"]["markers"]
    data = []
    for store in store_list:
        detail = bs(store["text"], "lxml")
        page_url = base_url + detail.select_one("a")["href"]
        location_name = detail.select_one("a").string.replace("&amp;", "&").strip()
        street_address = (
            detail.select_one("div.street-address").text.replace("\n", "").strip()
        )
        city = detail.select_one("span.locality").string
        state = detail.select_one("span.region").string
        zip = detail.select_one("span.postal-code").string
        phone = detail.select_one("div.tel span.value").string
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude = store["latitude"]
        longitude = store["longitude"]
        res1 = session.get(page_url)
        soup = bs(res1.text, "lxml")
        hours_of_operation = soup.select_one("div.store-hours li p").contents[0]

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
