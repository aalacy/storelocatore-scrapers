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
    locator_domain = "https://www.buildabear.co.uk/"
    api_url = "https://www.buildabear.co.uk/on/demandware.store/Sites-buildabear-uk-Site/en_GB/Stores-GetNearestStores?latitude=51.5073509&longitude=-0.1277583&countryCode=UK&distanceUnit=mi&maxdistance=2000"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["stores"].items()

    for _id, j in js:
        street_address = (
            f"{j.get('address1')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("stateCode") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = j.get("countryCode") or "<MISSING>"
        if country_code == "UK":
            country_code = "GB"
        else:
            continue
        store_number = _id
        page_url = f"https://www.buildabear.co.uk/locations?StoreID={_id}"
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        source = j.get("storeHours") or "<html></html>"
        tree = html.fromstring(source)
        hours = tree.xpath("//li")

        for h in hours:
            _tmp.append(" ".join("".join(h.xpath(".//text()")).split()))

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
