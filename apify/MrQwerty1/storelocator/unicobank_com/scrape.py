import csv
import re

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
    locator_domain = "https://unicobank.com/"
    page_url = "https://unicobank.com/locations/"
    country_code = "US"
    store_number = "<MISSING>"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[@class='fusion-fullwidth fullwidth-box fusion-builder-row-3 nonhundred-percent-fullwidth non-hundred-percent-height-scrolling fusion-equal-height-columns fusion-no-small-visibility']/div/div[.//img]"
    )

    for d in divs:
        location_name = "".join(d.xpath(".//h2/text()")).strip()
        lines = d.xpath(
            ".//div[@aria-labelledby='fusion-tab-contactinfo']/p[1]/text()|.//p[contains(text(), 'Physical Address')]/text()"
        )
        line = []
        for l in lines:
            if not l.strip():
                continue
            if "(" in l:
                break
            if "Physical" in l:
                line = []
                continue
            line.append(l.strip())

        street_address = ", ".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        try:
            state = line.split()[0]
            postal = line.split()[1]
        except IndexError:
            state = location_name.split(",")[-1].strip()
            postal = line

        try:
            phone = d.xpath(
                ".//p[contains(text(), 'Phone')]/text()|.//p[contains(text(), 'Tel')]/text()"
            )[0]
            phone = (
                phone.replace("Phone", "")
                .replace("Tel", "")
                .replace(":", "")
                .replace(".", "")
                .strip()
            )
        except IndexError:
            phone = "<MISSING>"

        text = "".join(d.xpath(".//script/text()"))

        latitude = "".join(re.findall(r'"latitude":"(\d{2}.\d+)"', text)) or "<MISSING>"
        longitude = (
            "".join(re.findall(r'"longitude":"(-?\d{2,3}.\d+)"', text)) or "<MISSING>"
        )
        location_type = "<MISSING>"

        hours = " ".join(
            d.xpath(".//p[./strong[contains(text(),'Lobby Hours')]]/text()")
        )
        hours = hours.replace("\n", "").replace("pm", "pm;").strip()
        if hours.endswith(";"):
            hours = hours[:-1]

        hours_of_operation = hours

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
