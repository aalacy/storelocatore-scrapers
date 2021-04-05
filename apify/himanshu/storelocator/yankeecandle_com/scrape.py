from sgrequests import SgRequests
import csv


def fetch_data():
    url = "https://storescontent.yankeecandle.com/searchQuery?radius=500000&lat=33.5973469&long=-112.1072528&storeType=2&origin=US"
    json_data = SgRequests().get(url).json()
    addresses = []
    for val in json_data["stores"]:
        store = []
        location_domain = "https://www.yankeecandle.com/"
        store.append(location_domain)
        store.append(val["label"] if val["label"] else "<MISSING>")
        store.append(val["address"] if val["address"] else "<MISSING>")
        store.append(val["city"] if val["city"] else "<MISSING>")
        store.append(val["state"]["abbr"] if val["state"]["abbr"] else "<MISSING>")
        store.append(val["zip"] if val["zip"] else "<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append(val["phone"] if val["phone"] else "<MISSING>")
        store.append("<MISSING>")
        store.append(val["lat"] if val["lat"] else "<MISSING>")
        store.append(val["long"] if val["long"] else "<MISSING>")
        hours_of_operation = " "
        for i in val["regHours"]:
            hours_of_operation = (
                hours_of_operation + i["day"] + " " + i["open"] + "-" + i["close"] + " "
            )
        store.append(hours_of_operation if hours_of_operation else "<MISSING>")
        store.append(location_domain + val["ctaUrl"])
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        yield store


def load_data(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def scrape():
    data = fetch_data()
    load_data(data)


if __name__ == "__main__":
    scrape()
