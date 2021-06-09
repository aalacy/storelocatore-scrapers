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

    locator_domain = "https://www.peoples.bank/"
    page_url = "https://www.peoples.bank/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    li = tree.xpath(
        '//ul[@class="accordion"]/li[position()>1]//div[@class="accordion-content"]//a[contains(text(), "View Map")]'
    )

    for l in li:
        location_name = "".join(l.xpath(".//preceding::h2[1]//text()")).strip()
        if not location_name:
            continue
        location_type = "<MISSING>"
        street_address = (
            "".join(l.xpath(".//preceding-sibling::text()[2]"))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>":
            street_address = (
                "".join(l.xpath(".//preceding::div[1]/text()"))
                .replace("\n", "")
                .strip()
            )
        if street_address.find("Little") != -1:
            street_address = "".join(l.xpath(".//preceding-sibling::span[1]/text()"))
        ad = (
            "".join(l.xpath(".//preceding-sibling::text()[1]"))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        phone = "".join(
            l.xpath(
                './/preceding::b[contains(text(), "PHONE")][1]/following-sibling::text()'
            )
        ).strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"

        text = "".join(l.xpath(".//@href"))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"

        tmp = []
        hours = l.xpath(".//following::table[1]//tr")
        for h in hours:
            day = "".join(h.xpath(".//th/text()"))
            time = "".join(h.xpath(".//td[1]/text()"))
            line = f"{day} {time}"
            tmp.append(line)
        hours_of_operation = ";".join(tmp) or "<MISSING>"

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
