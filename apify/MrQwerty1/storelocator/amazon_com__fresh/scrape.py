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


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]


def fetch_data():
    out = []
    locator_domain = "https://amazon.com/fresh"
    page_url = "https://www.amazon.com/fmc/m/20190651?almBrandId=QW1hem9uIEZyZXNo"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"
    country_code = "US"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = tree.xpath("//p[./a[contains(text(), 'Amazon Fresh store - ')]]//text()")
    text = list(filter(None, [t.strip() for t in text]))
    rows = chunks(text, 4)

    for r in rows:
        location_name = r[0]
        if r[-1].find("Store") != -1:
            hours_of_operation = r[-1].replace("Store hours ", "")
            street_address = r[1]
            r = r[2]
        else:
            hours_of_operation = "Coming Soon"
            street_address = r[2]
            r = r[3]

        city = r.split(",")[0].strip()
        r = r.split(",")[1].strip()
        state = r.split()[0]
        postal = r.split()[-1]

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
