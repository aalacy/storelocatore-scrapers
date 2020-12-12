import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("priceritemarketplace_com")
session = SgRequests()


def write_output(data):
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


def fetch_data():
    addresses = []
    base_url = "https://www.priceritemarketplace.com/"
    json_data = session.get(
        "https://storefrontgateway.brands.wakefern.com/api/near/40.8814882/-74.113198/10000/500/stores"
    ).json()

    for val in json_data["items"]:
        if "(Coming soon)" in val["name"] or "(Coming Soon)" in val["name"]:
            continue
        if "Dublin" in val["city"]:
            continue
        store = []
        store.append(base_url if base_url else "<MISSING>")
        store.append(val["name"] if val["name"] else "<MISSING>")
        store.append(val["addressLine1"] if val["addressLine1"] else "<MISSING>")
        store.append(val["city"] if val["city"] else "<MISSING>")
        store.append(
            val["countyProvinceState"] if val["countyProvinceState"] else "<MISSING>"
        )
        store.append(val["postCode"] if val["postCode"] else "<MISSING>")
        store.append("US")
        store.append(val["retailerStoreId"] if val["retailerStoreId"] else "<MISSING>")
        store.append(val["phone"] if val["phone"] else "<MISSING>")
        store.append("Price Rite")
        store.append(
            val["location"]["latitude"] if val["location"]["latitude"] else "<MISSING>"
        )
        store.append(
            val["location"]["longitude"]
            if val["location"]["longitude"]
            else "<MISSING>"
        )
        store.append(
            val["openingHours"].replace("\n", "")
            if val["openingHours"]
            else "<MISSING>"
        )
        store.append("<MISSING>")
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
