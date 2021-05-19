import csv

from lxml import html
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address, International_Parser


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
    locator_domain = "https://www.farmboy.ca/"
    api_url = "https://www.farmboy.ca/stores/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    articles = tree.xpath("//article[contains(@class, 'all portfolio-item')]")

    for a in articles:
        location_name = "".join(a.xpath(".//h3/text()")).strip()
        page_url = "".join(a.xpath(".//a[./img]/@href")) or "<MISSING>"
        line = a.xpath(".//div[@id='sin']/*[1]//text()")
        line = " ".join(list(filter(None, [l.strip() for l in line])))

        adr = parse_address(International_Parser(), line)
        street_address = (
            f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
                "None", ""
            ).strip()
            or "<MISSING>"
        )
        city = adr.city or "<MISSING>"
        state = adr.state or "<MISSING>"
        postal = adr.postcode or "<MISSING>"
        country_code = "CA"
        store_number = "<MISSING>"
        phone = (
            "".join(
                a.xpath(
                    ".//*[contains(text(), 'Phone') or contains(text(), 'Tel')]/text()"
                )
            )
            .replace("Phone", "")
            .replace("Tel", "")
            .replace(":", "")
            .strip()
            or "<MISSING>"
        )
        if phone.find("\n") != -1:
            phone = phone.split("\n")[0].strip()

        text = "".join(a.xpath(".//div[@id='mstore']/a[contains(@href, 'maps')]/@href"))
        try:
            latitude = text.split("@")[1].split(",")[0]
            longitude = text.split("@")[1].split(",")[0]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        tr = a.xpath(".//div[@id='sinfo']/table//tr")
        for t in tr:
            day = "".join(t.xpath("./td[1]/text()")).strip()
            time = "".join(t.xpath("./td[2]/text()")).replace("*", "").strip()
            _tmp.append(f"{day} {time}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
