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
    locator_domain = "https://jollibeeusa.com/"
    page_url = "https://jollibeeusa.com/locations/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    tr = tree.xpath("//table//tr[not(@class)]")

    for t in tr:
        line = t.xpath("./td[1]/text()")
        line = list(filter(None, [l.strip() for l in line]))
        location_name = "".join(t.xpath("./td[1]/a/text()")).strip()
        if not location_name:
            location_name = line[0]
            line = line[1:]

        if len(line) == 1:
            line = line[0].split(".")
            if len(line) == 1:
                line = line[0].replace(",", "*", 1)
                line = line.split("*")

        street_address = " ".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        state = "<MISSING>"
        postal = line.split()[-1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        page_url = "<MISSING>"
        phone = "".join(t.xpath("./td[3]/text()")).strip() or "<MISSING>"
        try:
            loc = "".join(t.xpath("./td[1]/a/@href")).split("@")[1].split(",")
            latitude = loc[0]
            longitude = loc[1]
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            "".join(t.xpath("./td[4]//text()")).replace("\n", ";").replace(":;", ":")
            or "<MISSING>"
        )

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
