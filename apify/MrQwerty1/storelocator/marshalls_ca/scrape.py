import csv
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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

        for row in data:
            writer.writerow(row)


def fetch_data():
    out = []
    locator_domain = "https://www.marshalls.ca/"
    api_url = "https://marketingsl.tjx.com/storelocator/GetAllStoresForChain"
    data = {"chain": "93", "lang": "en"}

    session = SgRequests()
    r = session.post(api_url, data=data)
    js = r.json()["Stores"]

    for j in js:
        street_address = (
            f"{j.get('Address')} {j.get('Address2') or ''}".replace("<br>", "").strip()
            or "<MISSING>"
        )
        city = j.get("City") or "<MISSING>"
        state = j.get("State") or "<MISSING>"
        postal = j.get("Zip") or "<MISSING>"
        country_code = j.get("Country") or "<MISSING>"
        store_number = j.get("StoreID") or "<MISSING>"
        location_name = j.get("Name")
        phone = j.get("Phone") or "<MISSING>"
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = j.get("Hours") or "<MISSING>"
        page_url = f"https://www.marshalls.ca/en/storelocator?store={store_number}"

        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
