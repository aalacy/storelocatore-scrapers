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
    url = "https://www.dunhamssports.com/"
    api_url = "https://www.dunhamssports.com/on/demandware.store/Sites-Dunhams-Site/en_US/Stores-GetInitialData"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["stores"]

    for j in js:
        locator_domain = url
        location_name = j.get("storeName")
        adr1 = j.get("address1")
        if adr1:
            if adr1[0].isdigit() or not j.get("address2"):
                street_address = (
                    f"{j.get('address1')} {j.get('address2') or ''}".strip()
                    or "<MISSING>"
                )
            else:
                street_address = j.get("address2") or "<MISSING>"
        else:
            street_address = "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("stateCode") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = "US"
        store_number = j.get("id") or "<MISSING>"
        page_url = (
            f" https://www.dunhamssports.com/weekly-ads.html?store_code={store_number}"
        )
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        text = j.get("storeHours") or "<html></html>"
        tree = html.fromstring(text)
        tr = tree.xpath("//tr")
        for t in tr:
            day = "".join(t.xpath("./td[1]/text()")).strip()
            time = (
                "".join(t.xpath("./td[2]/text()"))
                .replace("Open 1 Hour Early for Elderly/Vulnerable", "")
                .strip()
            )
            _tmp.append(f"{day} {time}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        if hours_of_operation.lower().count("closed") == 7:
            continue

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
