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
    locator_domain = "https://thepilatesbarre.com"
    api_url = "https://thepilatesbarre.com/contact/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath("//section[contains(@class, 'page-link-item')]")
    for b in block:

        page_url = "".join(b.xpath(".//@onclick")).split("'")[1].split("'")[0]

        location_name = "".join(b.xpath(".//h4/text()"))
        ad = (
            " ".join(b.xpath('.//section[@class="locatioAddress"]/p/text()'))
            .replace("\n", "")
            .strip()
        )
        street_address = ad.split(",")[0]
        city = ad.split(",")[0].split()[-1]
        if ad.find("6915") != -1:
            city = " ".join(ad.split(",")[0].split()[-2:])
            street_address = " ".join(ad.split(",")[0].split()[:-2])
        state = ad.split(",")[1].split()[0].strip()
        country_code = "US"
        postal = ad.split(",")[1].split()[-1].strip()
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        phone = "".join(b.xpath('.//a[contains(@href, "tel")]/text()'))

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
