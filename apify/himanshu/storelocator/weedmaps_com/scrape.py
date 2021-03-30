import csv
from sgrequests import SgRequests

session = SgRequests()
base_url = "https://weedmaps.com"


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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

        for row in data:
            writer.writerow(row)


def fetch_data():
    address = []
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
    }
    page = 1
    while True:
        loc_url = (
            "https://api-g.weedmaps.com/discovery/v2/listings?&filter%5Bbounding_radius%5D=75000000mi&filter%5Bbounding_latlng%5D=32.79148101806641%2C-86.82768249511719&latlng=32.79148101806641%2C-86.82768249511719&page_size=150&page="
            + str(page)
        )
        jd = session.get(loc_url, headers=headers).json()
        page += 1
        if "errors" in jd.keys():
            break
        for loc in jd["data"]["listings"]:
            store = []
            store.append(base_url)
            store.append(loc["name"] if loc["name"] else "<MISSING>")
            store.append(loc["address"] if loc["address"] else "<MISSING>")
            if len(store[2].split(":")) > 1:
                continue
            store.append(loc["city"] if loc["city"] else "<MISSING>")
            store.append(loc["state"] if loc["state"] else "<MISSING>")
            store.append(loc["zip_code"] if loc["zip_code"] else "<MISSING>")
            if store[5].isdigit():
                store.append("US")
            else:
                store.append("CA")
            store.append("<MISSING>")
            store.append(loc["phone_number"] if loc["phone_number"] else "<MISSING>")
            store.append(loc["type"] if loc["type"] else "<MISSING>")
            store.append(loc["latitude"] if loc["latitude"] else "<MISSING>")
            store.append(loc["longitude"] if loc["longitude"] else "<MISSING>")
            try:
                days = loc["business_hours"].keys()
                h_o_o = ""
                for day in days:
                    h_o_o = (
                        h_o_o
                        + " "
                        + day
                        + " "
                        + loc["business_hours"][day]["open"]
                        + "-"
                        + loc["business_hours"][day]["close"]
                    )
                store.append(h_o_o)
            except:
                store.append("<INACCESSIBLE>")
            store.append(loc["web_url"] if loc["web_url"] else "<MISSING>")

            if store[2] in address:
                continue
            address.append(store[2])

            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
