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
    locator_domain = "https://www.brightstar.com/"
    page_url = "https://www.brightstar.com/contact-us/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='col-xs-12 col-md-12']/article")

    for d in divs:
        location_name = "".join(d.xpath("./h2/text()")).strip()
        phone = "<MISSING>"

        _tmp = []
        lines = d.xpath("./p/text()")
        black_list = ["Brightstar", "E-mail:", "Website", "普", "@brightstar.com"]
        for line in lines:
            skip = False
            for black in black_list:
                if black in line:
                    skip = True
                    break
            if skip:
                continue
            _tmp.append(line.strip())

        if not _tmp:
            continue

        p = _tmp[-1].lower()
        if "china" in p or "kista" in p or "oslo" in p:
            pass
        elif "phone" in p or "tel" in p or p[0].isdigit() or p[0] == "(":
            phone = _tmp.pop()
            if ":" in phone:
                phone = phone.split(":")[-1].strip()
            if "|" in phone:
                phone = phone.split("|")[-1].strip()

        line = ", ".join(_tmp)
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
        country_code = "<MISSING>"
        store_number = "<MISSING>"
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
