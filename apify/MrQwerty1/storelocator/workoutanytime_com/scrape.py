import csv
import json

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
    url = "https://www.workoutanytime.com/"
    api_url = "https://www.workoutanytime.com/locations"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    text = (
        "".join(tree.xpath("//script[contains(text(), 'storeDataAry')]/text()"))
        .split(" = ")[1]
        .split(";\n")[0]
    )
    js = json.loads(text)

    for j in js:
        locator_domain = url
        adr = (
            j.get("address")
            .replace("\n", "")
            .replace("\r", "")
            .replace("<br/>", "<br />")
            .split("<br />")
        )
        if len(adr) == 2:
            street_address = adr[0]
        else:
            street_address = " ".join(adr[:2])
        adr = adr[-1]
        city = adr.split(",")[0]
        adr = adr.split(",")[1].strip()
        state = adr.split()[0]
        postal = adr.split()[-1]
        country_code = "US"
        store_number = j.get("club_id") or "<MISSING>"
        page_url = f'https://workoutanytime.com/{j.get("slug")}/'
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("hours", "").split("<br />") or []
        for h in hours:
            if (h.find(":") != -1 or h.find("-") != -1) and h.find("hours") == -1:
                _tmp.append(h.strip())

        hours_of_operation = ";".join(_tmp).replace("<br/>", ";") or "<MISSING>"

        if j.get("status") == "coming_soon" or j.get("status") == "presales":
            hours_of_operation = "Coming Soon"

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
