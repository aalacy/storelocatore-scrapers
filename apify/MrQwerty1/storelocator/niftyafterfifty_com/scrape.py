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
    locations = []
    locator_domain = "https://www.niftyafterfifty.com/"
    page_url = "https://www.niftyafterfifty.com/locations"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = tree.xpath("//p[@class='font_8']//text()")
    text = list(filter(None, [t.strip() for t in text]))
    _tmp = []
    for t in text:
        if "\u200b" in t or "PT Hours" in t or "Nifty" in t or "fax" in t:
            continue
        if "__" in t or "Northern" in t:
            continue
        if t.startswith("(") and t.endswith(")"):
            continue

        if t.split()[0].strip().isupper():
            if len(_tmp) > 1:
                locations.append(_tmp)
            _tmp = []

        _tmp.append(t)
    else:
        locations.append(_tmp)

    locations.pop(0)
    for loc in locations:
        location_name = loc.pop(0)
        street_address = loc.pop(0)
        line = loc.pop(0).replace(",", "")
        state = line.split()[-2]
        postal = line.split()[-1]
        city = line.replace(state, "").replace(postal, "").strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = loc.pop(0).replace("ph", "").strip()
        if "ext" in phone:
            phone = phone.split("ext")[0].strip()
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            " ".join(" ".join(loc).replace("Hours:", "").replace("Fitness", "").split())
            or "<MISSING>"
        )
        if " to " in hours_of_operation:
            hours_of_operation = hours_of_operation.split(" to ")[0].strip()

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
