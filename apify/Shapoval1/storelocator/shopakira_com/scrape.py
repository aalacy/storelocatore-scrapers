import csv
from lxml import html
from sgrequests import SgRequests
import json


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
    locator_domain = "https://www.shopakira.com"
    page_url = "https://www.shopakira.com/store-locator/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(.,'var locations = [')]/text()"))
    text = text.split("var locations = [")[1]
    text = "[" + text.split("];")[0] + "]"

    js = json.loads(text)
    for j in js:

        tmp = []
        street_address = "".join(j.get("address")) or "<MISSING>"
        city = j.get("district") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = "".join(j.get("postal_code")) or "<MISSING>"
        if postal == "60602":
            street_address = "".join(street_address.split(".")[:-1])
        elif postal == "60173":
            street_address = " ".join(street_address.split()[:-2])

        country_code = j.get("country")
        if country_code == "United States":
            country_code = "US"

        store_number = j.get("gmapstrlocator_id")
        location_name = (
            "".join(j.get("store_name")) + " - " + "".join(j.get("store_identifier"))
        )
        phone = "".join(j.get("store_phone"))
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        loc = j.get("attributes_list") or "<MISSING>"
        if loc != "<MISSING>":
            loc = "".join(loc).split("<span>")[1].split("</span>")[0]
        loc = loc.split("<")[0]
        location_type = loc or "<MISSING>"
        hours = "".join(j.get("store_description"))
        divs = html.fromstring(hours)
        for d in divs:
            day = d.xpath("//p/text()")
            day = " ".join(list(filter(None, [a.strip() for a in day])))
            line = f"{day}"
            tmp.append(line)

        hours_of_operation = ";".join(tmp) or "<MISSING>"
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
