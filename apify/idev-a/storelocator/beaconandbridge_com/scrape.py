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
    base_url = "http://beaconandbridge.com"
    res = session.get("http://beaconandbridge.com/locations/")
    soup = bs(res.text, "lxml")
    store_list = soup.select("div#section_2 div.the_list_wrap")
    data = []
    for store in store_list:
        page_url = "http://beaconandbridge.com/locations"
        location_name = store.select_one("h3.the_list_item_headline").string
        address_detail = store.select_one("a[target='_blank']").contents
        address_detail = [x for x in address_detail if x.string]
        street_address = address_detail[0]
        city = address_detail[1].split(", ")[0]
        state = address_detail[1].split(", ")[1]
        zip = address_detail[2]
        contents = store.select("div.the_list_item_desc p")
        contents = [x for x in contents if x.text]
        contents = [x for x in contents[0].contents if x.string]
        phone = contents[0].replace("PHONE: ", "")
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        contents = contents[1:]
        hours_of_operation = (
            store.text.split("HOURS:")[1]
            .split("Temporary")[0]
            .split("As")[0]
            .replace("\n", " ")
            .replace("Current:", " ")
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
