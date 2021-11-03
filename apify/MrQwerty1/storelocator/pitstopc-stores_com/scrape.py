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


def get_coords():
    coords = []
    session = SgRequests()
    r = session.get(
        "https://www.google.com/maps/d/u/0/kml?mid=16SO1IYTK6nn7HGLwAHFWH14ijkE&forcekml=1"
    )
    tree = html.fromstring(r.content)
    markers = tree.xpath("//coordinates/text()")
    for m in markers:
        m = m.replace(",0", "")
        lng, lat = m.split(",")
        coords.append((lat.strip(), lng.strip()))

    return coords


def fetch_data():
    out = []
    coords = get_coords()
    locator_domain = "https://www.pitstopc-stores.com/"
    page_url = "https://www.pitstopc-stores.com/store-locations"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = tree.xpath("//p[@class='font_8']//text()")
    text = list(filter(None, [t.strip() for t in text]))

    cnt = 0
    for t in text:
        if "zip" not in t:
            cnt += 1
            continue

        location_name = text[cnt - 1]
        line = text[cnt]
        street_address = line.split("zip")[0].replace(",", "").strip()
        city = location_name.split(",")[0].strip()
        state = location_name.split(",")[1].strip()
        postal = line.split("zip")[-1]
        if "(" in postal:
            postal = (postal.split("(")[0] + postal.split(")")[1]).strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = text[cnt + 1]
        latitude, longitude = coords.pop(0)
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        cnt += 1

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
