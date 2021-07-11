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

    locator_domain = "https://myyabos.com/"
    api_url = "https://myyabos.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[./p/strong[contains(text(), "Open")]] | //div[./p/strong[contains(text(), "Closed")]]'
    )
    for d in div:
        page_url = "https://myyabos.com/locations/"
        location_name = "".join(d.xpath(".//h4/text()"))
        location_type = "<MISSING>"
        street_address = (
            " ".join(d.xpath('.//p/a[contains(@href, "goo")]/text()')) or "<MISSING>"
        )
        if street_address == "<MISSING>":
            street_address = "".join(d.xpath(".//p[2]/text()[1]"))
        ad = "".join(d.xpath('.//p[./a[contains(@href, "goo")]]/text()')) or "<MISSING>"
        if street_address.find("5242") != -1:
            street_address = " ".join(street_address.split()[:3])
            ad = " ".join(d.xpath('.//p/a[contains(@href, "goo")]/text()'))
            ad = " ".join(ad.split()[3:])
        if ad == "<MISSING>":
            ad = "".join(d.xpath(".//p[2]/text()[2]"))
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()')) or "<MISSING>"
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/strong[contains(text(), "Kitchen Hours:")]/following-sibling::text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        cls = "".join(d.xpath('.//strong[contains(text(), "Closed")]/text()'))
        if cls:
            hours_of_operation = "Closed"

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
