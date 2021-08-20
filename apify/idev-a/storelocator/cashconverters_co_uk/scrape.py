import csv
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
    base_url = "https://www.cashconverters.co.uk"
    data = []
    for x in range(1, 23):
        url = (
            "https://www.cashconverters.co.uk/store-locator?show-all-stores=&page="
            + str(x)
            + "#store-results"
        )
        res = session.get(url)
        store_links = bs(res.text, "lxml").select("div.store-result a")

        for store_link in store_links:
            page_url = base_url + store_link["href"]
            res1 = session.get(page_url)
            store = bs(res1.text, "lxml")
            address_detail = (
                store.select_one("div.store-panel-info").select("p")[0].text.split(", ")
            )
            zip_city = address_detail.pop().split(" ")
            if len(zip_city) == 2:
                zip = "<MISSING>"
                city = " ".join(zip_city)
            elif len(zip_city) == 1:
                city = zip_city.pop()
                zip_city = address_detail.pop().split(" ")
                zip = " ".join(zip_city[:2])
                city = " ".join(zip_city[2:]) if len(zip_city) > 2 else city
            else:
                city = " ".join(zip_city[2:])
                zip = " ".join(zip_city[:2])
            state = "<MISSING>"
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            location_name = store.select_one("h2").text
            street_address = ", ".join(address_detail)
            phone = (
                store.select_one("div.store-panel-info")
                .select("p")[1]
                .contents[1]
                .text.split("/")[0]
                .strip()
            )
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"

            hours = (
                store.select_one("div.store-panel-info").select("p")[2].text.split("\n")
            )

            keyword_list = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

            hours_of_operation = ""
            for x in hours:
                if any(s in x for s in keyword_list):
                    hours_of_operation += x.strip() + " "
                elif x.strip().lower().islower() is False:
                    hours_of_operation += x.strip() + " "
            hours_of_operation = hours_of_operation.strip()
            hours_of_operation = (
                hours_of_operation.replace("Click and Collect", "")
                or "Temporarily closed"
            )
            if "now closed" in "".join(hours):
                continue

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
