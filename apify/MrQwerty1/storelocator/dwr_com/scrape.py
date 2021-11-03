import csv

from lxml import html
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
    locator_domain = "https://www.dwr.com/"
    api_url = "https://www.dwr.com/on/demandware.store/Sites-dwr-Site/en_US/Stores-FindStores?showMap=false&radius=10000&lat=37.090194&long=-95.712889"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["stores"]

    for j in js:
        street_address = (
            f"{j.get('address1')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("stateCode") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = j.get("countryCode") or "<MISSING>"
        store_number = j.get("ID") or "<MISSING>"
        page_url = f"https://www.dwr.com/store?lang=en_US&StoreId={store_number}"
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        text = j.get("storeHours") or "<html></html>"
        tree = html.fromstring(text)
        tr = tree.xpath(".//tr[./td]")
        for t in tr:
            day = "".join(t.xpath("./td[1]/text()")).strip()
            time = "".join(t.xpath("./td[2]/text()")).strip()
            _tmp.append(f"{day}: {time}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

        if not (country_code == "US" or country_code == "CA"):
            continue

        if street_address.find("(") != -1:
            street_address = street_address.split("(")[0].strip()

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
