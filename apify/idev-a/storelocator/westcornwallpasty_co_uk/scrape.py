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


def remove_empty_string_from_array(param):
    data = param
    while True:
        try:
            data.remove("")
        except:
            return data


def fetch_data():
    base_url = "http://westcornwallpasty.co.uk"
    res = session.get("http://westcornwallpasty.co.uk/visit-us")
    soup = bs(res.text, "lxml")
    store_list = soup.select("div.storeLocator div#list_view ul.listView ul li")
    data = []
    for store in store_list:
        page_url = "<MISSING>"
        location_name = store.select_one("a").string.strip()
        if "\r\n" in store.select_one("p").string:
            address = store.select_one("p").string.split("\r\n")
        else:
            address = store.select_one("p").string.split(", ")
        address = remove_empty_string_from_array(address)
        zip = address.pop()
        zip_data = zip.split(" ")
        zip_data = remove_empty_string_from_array(zip_data)
        if len(zip_data) > 2:
            zip = " ".join(zip_data[-2:])
            city = " ".join(zip_data[:-2])
        else:
            city = address.pop()
        city = city[:-1] if city.endswith(",") else city
        state = "<MISSING>"
        street_address = " ".join(address)
        country_code = "UK"
        store_number = "<MISSING>"
        try:
            phone = store.select_one("a.visitUsTel").string.replace("Tel: ", "")
        except:
            phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = (
            store.select_one("div.openingTimes")
            .text.replace("\n\n\n", " ")
            .replace("\n", " ")
            .strip()
        )
        hours_of_operation = (
            "<MISSING>" if hours_of_operation == "" else hours_of_operation
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
