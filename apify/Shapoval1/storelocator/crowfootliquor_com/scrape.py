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

    locator_domain = "https://crowfootliquor.com"
    page_url = "https://crowfootliquor.com/locations/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    session = SgRequests()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="entry"]/section[position()>1]')

    for d in div:

        location_name = "".join(d.xpath(".//h3/text()")).strip()
        if location_name.find("Aspen Wine & Spirits") != -1:
            continue

        location_type = "Crowfoot Wine & Spirits"
        street_address = " ".join(
            d.xpath('.//p[./a[contains(@href, "goo")]]/a/text()')
        ).strip()
        ad = (
            " ".join(d.xpath('.//p[./a[contains(@href, "goo")]]/text()'))
            .replace("\n", "")
            .strip()
        )
        if location_name.find("Altadore") != -1:
            ad = "Calgary, AB T2T 3W2"
        phone = (
            "".join(d.xpath('.//p[contains(text(), "Phone")]/text()'))
            .replace("Phone:", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = " ".join(ad.split(",")[1].split()[1:]).strip()
        country_code = "CA"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        map_link = "".join(d.xpath(".//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        hours_of_operation = (
            " ".join(
                d.xpath('.//p[contains(text(), "Phone")]/following-sibling::p//text()')
            )
            .replace("\n", " ")
            .strip()
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
