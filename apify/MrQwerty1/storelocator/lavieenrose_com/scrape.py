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
    locator_domain = "https://www.lavieenrose.com/"
    api_url = "https://www.lavieenrose.com/en/stores/ajax/getAllStores"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["items"]

    for j in js:
        street_address = (
            f"{j.get('addressLine1')} {j.get('addressLine2') or ''}".strip()
            or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("provinceEnglish") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = "CA"
        store_number = j.get("identifier") or "<MISSING>"
        slug = j.get("urlKey")
        page_url = f"https://www.lavieenrose.com/en/our-stores/{slug}"
        location_name = j.get("name")
        phone = j.get("phoneNumber") or "<MISSING>"
        if phone == "TBD":
            phone = "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        if j.get("storeTypeOutlet") == "1":
            location_type = "Outlet"
        else:
            location_type = "Store"

        _tmp = []
        source = j.get("hoursEnglish") or "<html></html>"
        tree = html.fromstring(source)
        tr = tree.xpath("//tr")
        for t in tr:
            day = "".join(t.xpath("./td[1]//text()")).strip()
            time = "".join(t.xpath("./td[2]//text()")).strip()
            _tmp.append(f"{day}: {time}")

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
