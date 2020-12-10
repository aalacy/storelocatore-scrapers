import csv

from sgrequests import SgRequests
from lxml import html


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


def generate_ids():
    session = SgRequests()
    r = session.get("https://www.quicklane.com/en-us/service-centers")
    tree = html.fromstring(r.text)
    out = []
    ids = tree.xpath("//h5/a[@class='store-url']/@href")
    for i in ids:
        out.append(i.split("/")[-1])
    return out


def fetch_data():
    out = []
    url = "https://www.quicklane.com/en-us/service-centers"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
        "Origin": "https://www.quicklane.com",
    }
    ids = generate_ids()

    for i in ids:
        r = session.get(
            f"https://www.digitalservices.ford.com/ql/api/v2/dealer?dealer={i}",
            headers=headers,
        )
        js = r.json()["qlDealer"]
        if not js.get("dealer"):
            continue
        s = js.get("seo", {}).get("quickLaneInfo") if js.get("seo") else {}
        if not s:
            s = {}
        j = js.get("dealer")
        locator_domain = url
        street_address = j.get("streetAddress") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        location_name = j.get("dealerName") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = j.get("country", "").replace("USA", "US") or "<MISSING>"
        store_number = i
        page_url = (
            f"https://www.quicklane.com/en-us/oil-change-tire-auto-repair-store/"
            f"{state}/{city}/{postal}/-/{i}"
            or "<MISSING> "
        )

        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        for cnt in range(1, 5):
            key = f"hours{cnt}"
            val = s.get(key, "")
            if val:
                _tmp.append(val)

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
