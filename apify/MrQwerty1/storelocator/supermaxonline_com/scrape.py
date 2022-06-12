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
    locator_domain = "https://www.supermaxonline.com/"
    page_url = "https://www.supermaxonline.com/localidades.html"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[contains(@class,'col-md-4 localidades')]")

    for d in divs:
        location_name = "".join(d.xpath("./div/p[1]/strong/text()")).strip()
        lines = d.xpath("./div/p[last()]/text()")
        lines = list(filter(None, [l.strip() for l in lines]))
        index = 0
        for l in lines:
            if "Tel" in l:
                break
            index += 1

        phone = lines[index].replace("Tel.", "").strip()
        line = ", ".join(lines[:index])
        p = lines[index - 1].split()[-1]
        s = lines[index - 1].split()[-2]

        adr = parse_address(International_Parser(), line, postcode=p, state=s)
        street_address = (
            f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
                "None", ""
            ).strip()
            or "<MISSING>"
        )

        city = adr.city or "<MISSING>"
        state = adr.state or "<MISSING>"
        postal = adr.postcode or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"

        cl = "".join(d.xpath("./@class"))
        if "doscuatro" in cl:
            hours_of_operation = "24 hours"
        else:
            _tmp = []
            hours = lines[index + 1 :]
            for h in hours:
                if "fax" in h.lower():
                    continue
                _tmp.append(
                    h.replace("Dom", "Sunday")
                    .replace("L-S", "Monday-Saturday")
                    .replace("L-D", "Monday-Sunday")
                    .replace(".", "")
                )

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
