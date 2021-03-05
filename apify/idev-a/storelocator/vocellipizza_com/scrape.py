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
    base_url = "https://www.vocellipizza.com"
    res = session.get(base_url)
    region_list = (
        res.text.split("Select a State</option>")[1]
        .split("</select>")[0]
        .split("<option value='")[1:]
    )
    data = []

    for region in region_list:
        res = session.post(
            "https://www.vocellipizza.com/Locations-amp-Offers",
            data={"state": region.split("'")[0]},
        )
        soup = bs(res.text, "lxml")
        store_list = soup.select("div.location")
        for store in store_list:
            phone = store.select_one(".tel").string
            page_url = base_url + store.select_one(".location-nav a")["href"]
            res1 = session.get(page_url)
            soup1 = bs(res1.text, "lxml")
            street_address = soup1.select_one("span[itemprop='streetAddress']").string
            street_address = street_address.split(", ")
            while True:
                try:
                    street_address.remove("")
                except:
                    break
            street_address = ", ".join(street_address)
            if street_address.endswith(","):
                street_address = street_address[:-1]
            location_name = store.select_one(".org").string
            city = store.select_one(".locality").string
            zip = store.select_one(".postal-code").string
            state = store.select_one(".region").string
            country_code = "US"
            latitude = store.select_one(".gmap-small")["data-lat"]
            longitude = store.select_one(".gmap-small")["data-lon"]
            location_type = "<MISSING>"
            store_number = "<MISSING>"
            res1 = session.get(page_url)
            soup1 = bs(res1.text, "lxml")
            hours = soup1.select("p[itemprop='openingHours']")
            hours_of_operation = ""
            for hour in hours:
                hours_of_operation += hour.text + " "

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
