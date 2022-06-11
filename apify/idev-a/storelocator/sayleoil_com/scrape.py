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
    base_url = "https://www.sayleoil.com"
    res = session.get("https://www.sayleoil.com/location-category/")
    store_links = (
        bs(res.text, "lxml")
        .select_one("li#menu-item-286")
        .select("ul.sub-menu li a")[:-1]
    )
    data = []
    for store_link in store_links:
        link = store_link["href"]
        location_type = store_link.string
        res = session.get(link)
        store_list = bs(res.text, "lxml").select("div.fl-html div.row")
        for store in store_list:
            page_url = "https://www.sayleoil.com/location-category/"
            location_name = (
                store.select_one("h2.loc-title")
                .string.replace("’", "'")
                .replace("–", "-")
            )
            contents = store.select_one("div.loc-addr p").contents
            address_data = []
            for x in contents:
                if x.string is not None and x.string != "\n":
                    address_data.append(x.string.replace("\n", " ").strip())
            address_detail = address_data.pop()
            street_address = address_data[0].strip()
            street_address = (
                street_address[:-1] if street_address.endswith(",") else street_address
            )
            if len(address_detail.split(", ")) == 3:
                city = address_detail.split(", ")[0]
                state = address_detail.split(", ")[1]
                zip = address_detail.split(", ")[2]
            else:
                if len(address_detail.split(", ")) == 1:
                    tmp = address_detail.split(" ")
                    zip = tmp.pop()
                    state = tmp.pop()
                    city = tmp.pop()
                else:
                    if len(address_detail.split(", ")[1]) < 7:
                        zip = address_detail.split(", ")[1]
                        state_city = address_detail.split(", ")[0].split(" ")
                        state = state_city.pop()
                        city = " ".join(state_city)
                    else:
                        city = address_detail.split(", ")[0]
                        state = address_detail.split(", ")[1].split(" ")[0]
                        zip = address_detail.split(", ")[1].split(" ")[1]
            phone = store.select_one("div.loc-meta").text.split("Phone: ")[1]
            phone = phone.split("/")[0].strip()
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            if (
                len(store.select_one("div.loc-meta").text.split("Hours of Operation:"))
                == 1
            ):
                hours_of_operation = "<MISSING>"
            else:
                hours_of_operation = (
                    store.select_one("div.loc-meta")
                    .text.split("Hours of Operation:")[1]
                    .split("Phone: ")[0]
                    .replace("–", "-")
                    .replace("\n", " ")
                    .replace("for your convenience!", "")
                    .replace("New COVID-19 Hours", "")
                    .replace("New Covid-19 Hours", "")
                    .replace("COVID-19 Hours", "")
                    .strip()
                )

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
