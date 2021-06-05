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


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_coords(page_url):
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//iframe/@src"))

    return get_coords_from_embed(text)


def fetch_data():
    out = []
    locator_domain = "https://www.cinemacafe.com/"
    api_url = "https://www.cinemacafe.com/locations"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//article/p")

    for d in divs:
        location_name = "".join(d.xpath("./strong/span/a/text()")).strip()
        slug = "".join(d.xpath("./strong/span/a/@href"))
        page_url = f"https://www.cinemacafe.com{slug}"

        line = d.xpath("./text()")
        line = list(filter(None, [l.strip() for l in line]))

        phone = line.pop().replace("Phone:", "").strip()
        street_address = ", ".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = page_url.split("/")[-2]
        latitude, longitude = get_coords(page_url)
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

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
