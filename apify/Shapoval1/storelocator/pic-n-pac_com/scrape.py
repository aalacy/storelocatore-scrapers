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

    locator_domain = "https://pic-n-pac.com/"
    page_url = "https://pic-n-pac.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[contains(@id, "contact-info")] | //div[contains(@id, "site-links")]'
    )
    for d in div:

        location_name = "".join(
            d.xpath('.//div[@class="fl-rich-text"]/p/text()')
        ).replace("#16", " #16")
        location_type = "<MISSING>"
        street_address = "".join(d.xpath('.//a[contains(@href, "goo.gl")]/text()[1]'))
        ad = (
            " ".join(d.xpath('.//a[contains(@href, "goo.gl")]/text()[2]'))
            .replace("\n", "")
            .replace("Schertz,", "Schertz")
            .replace("Seguin.", "Seguin,")
            .replace("Schertz", "Schertz,")
            .strip()
        )
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()')) or "<MISSING>"

        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[-1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = location_name.split("#")[1].strip()
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
