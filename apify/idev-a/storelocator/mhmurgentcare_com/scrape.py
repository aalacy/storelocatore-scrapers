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
    base_url = "https://www.mhmurgentcare.com"
    res = session.get("https://www.mhmurgentcare.com/locations/")
    soup = bs(res.text, "lxml")
    store_list = soup.select(
        "div.elementor-element-787e8be div.elementor-widget-wrap div.elementor-element"
    )
    store_contact = soup.select(
        "div.elementor-element-37a16e6 div.elementor-widget-wrap div.elementor-element"
    )
    idx = 0
    data = []
    while idx < len(store_list):
        address = []
        for x in store_contact[idx].select_one("p").contents:
            if x.string is not None and x.string != "\n":
                address.append(x.string)
        address_detail = address.pop()
        street_address = " ".join(address).replace("Address", "").strip()
        city = address_detail.split(", ")[0]
        state = address_detail.split(", ")[1].split(" ")[0]
        state = state[:-1] if state.endswith(".") else state
        zip = address_detail.split(", ")[1].split(" ")[1]
        location_name = store_list[idx].select_one("p").contents[::2][0].string
        phone = (
            store_list[idx]
            .select_one("p")
            .contents[::2][1]
            .string.replace("Phone: ", "")
        )
        page_url = store_list[idx].select_one("a")
        if page_url is None:
            page_url = "<MISSING>"
            hours_of_operation = "<MISSING>"
        else:
            page_url = page_url["href"]
            res = session.get(page_url)
            soup = bs(res.text, "lxml")
            hours_of_operation = (
                soup.select_one("div.elementor-text-editor")
                .text.split("HOURS OF OPERATION")
                .pop()
                .replace("–", "-")
            )
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        idx += 1

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
