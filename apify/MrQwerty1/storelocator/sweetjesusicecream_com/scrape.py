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
    locator_domain = "https://www.sweetjesusicecream.com/"
    page_url = "https://www.sweetjesusicecream.com/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='loc-row']")

    for d in divs:
        location_name = "".join(d.xpath(".//h4/a/text()")).strip()
        line = d.xpath(".//div[@class='loc-col address-col']/p/text()")
        line = list(filter(None, [l.strip() for l in line]))
        if len(line) == 1:
            line = line[0].split("\n")

        street_address = ", ".join(line[:-1]).strip()
        line = line[-1]
        city = line.split(",")[0].strip()
        state = line.split(",")[1].strip()
        postal = "<MISSING>"
        country_code = "CA"
        if state == "CA":
            country_code = "US"

        store_number = "<MISSING>"
        phone = (
            "".join(d.xpath(".//div[@class='loc-col']/p/a/text()")).strip()
            or "<MISSING>"
        )
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = d.xpath(".//div[@class='loc-col']/p[./strong]")
        for h in hours:
            text = " ".join("".join(h.xpath(".//text()")).split())
            if "SEE" in text:
                _tmp.append("<MISSING>")
                break
            if text:
                _tmp.append(text)

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
