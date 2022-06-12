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
    locator_domain = "https://www.centralbank.net"
    api_url = "https://www.centralbank.net/API/ES/BranchLocation/Post"

    data = {
        "PageNumber": "1",
        "PageSize": "5000",
        "Distance": "5000",
        "Address": "238 Madison St, Jefferson City, MO 65101",
    }

    session = SgRequests()
    r = session.post(api_url, data=data)
    js = r.json()["results"]

    for j in js:
        a = j.get("address")
        street_address = (
            f"{a.get('address1')} {a.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("zipCode") or "<MISSING>"
        country_code = "US"
        store_number = j.get("contentId") or "<MISSING>"
        slug = j.get("url")
        page_url = f"{locator_domain}{slug}"
        location_name = j.get("title")
        phone = j.get("displayPhone") or "<MISSING>"
        if "ext" in phone:
            phone = phone.split("ext")[0].strip()
        loc = j.get("coordinates")
        latitude = loc.get("latitude") or "<MISSING>"
        longitude = loc.get("longitude") or "<MISSING>"
        if j.get("isBranch"):
            location_type = "Branch"
        else:
            continue

        source = j.get("description") or "<html></html>"
        tree = html.fromstring(source)
        hours = " ".join(
            " ".join(
                tree.xpath(
                    "//p[./u[contains(text(), 'Lobby')]]/text()|//h2[./u[text()='Hours:']]/following-sibling::p[1]/text()"
                )
            ).split()
        )
        if "Office Hours:" in source and not hours:
            hours = " ".join(
                "".join(tree.xpath("//text()"))
                .replace("Office Hours:", "")
                .replace("MST", "")
                .split()
            )
        if not hours:
            hours = " ".join(
                "".join(tree.xpath("//text()")).replace("Hours:", "").split()
            )
        hours = hours.replace(".", "").replace(" to ", " - ").replace("pm ", "pm; ")

        hours_of_operation = hours or "<MISSING>"

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
