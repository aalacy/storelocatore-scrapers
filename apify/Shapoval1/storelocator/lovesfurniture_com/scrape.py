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

    locator_domain = "https://lovesfurniture.com/"
    page_url = "https://lovesfurniture.com/store-locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="contactus"]')

    for d in div:

        location_name = "".join(d.xpath('./div[@class="contactLeft"]/h3/text()'))
        location_type = "<MISSING>"
        street_address = (
            "".join(d.xpath('./div[@class="contactLeft"]/p[1]/text()[1]'))
            .replace(",", "")
            .strip()
        )
        ad = (
            "".join(d.xpath('./div[@class="contactLeft"]/p[1]/text()[2]'))
            .replace("\n", "")
            .strip()
        )

        phone = "".join(
            d.xpath('.//p[./strong[contains(text(), "PHONE")]]/text()')
        ).strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[-1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        if street_address.find("1340") != -1:
            state = ad.split(",")[2].split()[0].strip()
            postal = ad.split(",")[2].split()[-1].strip()
            country_code = "US"
            city = ad.split(",")[1].strip()
            street_address = street_address + " " + ad.split(",")[0].strip()

        store_number = "<MISSING>"
        map_link = "".join(d.xpath(".//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        hours_of_operation = (
            " ".join(d.xpath('.//p[./strong[contains(text(), "HOURS")]]/text()'))
            .replace("\n", "")
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
