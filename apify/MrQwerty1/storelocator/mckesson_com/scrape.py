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
    locator_domain = "https://www.mckesson.com/"
    page_url = "https://www.mckesson.com/Contact-Us/Corporate-Contacts/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='contact-info']")

    for d in divs:
        location_name = "".join(d.xpath("./h5/text()")).strip()
        line = d.xpath("./ul/li/a/text()")
        line = list(filter(None, [l.strip() for l in line]))
        if "@" in line[-1]:
            continue

        street_address = " ".join(line[:-1])
        if street_address.endswith(","):
            street_address = street_address[:-1]
        line = line[-1].split(",")
        city = line[0].strip()
        state = line[1].strip()
        postal = line[2].strip()
        country_code = "US"
        if "Canada" in postal:
            postal = postal.replace("Canada", "").strip()
            country_code = "CA"

        store_number = "<MISSING>"
        try:
            phone = d.xpath(".//a[@class='ttc-phone']/text()")[0].strip()
        except IndexError:
            phone = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
