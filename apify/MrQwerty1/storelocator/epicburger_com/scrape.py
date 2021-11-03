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


def get_coords_from_google_url(url):
    try:
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def fetch_data():
    out = []
    locator_domain = "https://www.epicburger.com/"
    page_url = "https://www.epicburger.com/locations"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@role='gridcell']")

    for d in divs:
        location_name = "".join(d.xpath(".//h6/span/text()")).strip()
        line = d.xpath(".//text()")
        line = list(filter(None, [l.strip() for l in line]))
        index = line.index("PHONE")

        street_address = line[index - 2]
        csz = line[index + 1]
        city = csz.split(",")[0].strip()
        csz = csz.split(",")[1].strip()
        state = csz.split()[0]
        postal = csz.split()[-1]
        country_code = "US"
        store_number = "<MISSING>"
        phone = line[index - 1]

        text = "".join(d.xpath(".//a[contains(@href, 'google')]/@href"))
        latitude, longitude = get_coords_from_google_url(text)
        location_type = "<MISSING>"
        _tmp = []
        for h in line[line.index("EMAIL") + 1 :]:
            if h[0].isdigit():
                _tmp.append(f"{h};")
            else:
                _tmp.append(f"{h}: ")

        hours_of_operation = "".join(_tmp) or "<MISSING>"
        if "soon" in location_name.lower():
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
