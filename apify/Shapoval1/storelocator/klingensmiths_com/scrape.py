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

    locator_domain = "https://www.klingensmiths.com"
    api_url = "https://www.klingensmiths.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[@class="et_pb_button et_pb_more_button et_pb_button_one"]')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1/text()"))
        ad = "".join(tree.xpath("//h1/following-sibling::p[1]/text()"))

        location_type = "<MISSING>"
        street_address = ad.split(",")[0].strip()

        phone = (
            " ".join(
                tree.xpath(
                    '//h3[contains(text(), "Pharmacy Hours")]/following-sibling::p[./strong[contains(text(), "Phone")]]/text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
        )

        state = ad.split(",")[-1].split()[0].strip()
        postal = ad.split(",")[-1].split()[-1].strip()
        country_code = "USA"
        city = ad.split(",")[1].split(",")[0].strip()
        if street_address.find("316") != -1:
            street_address = " ".join(ad.split(",")[:2]).strip()
            city = ad.split(",")[2].split(",")[0].strip()

        store_number = "<MISSING>"
        map_link = "".join(tree.xpath("//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h3[contains(text(), "Pharmacy Hours")]/following-sibling::p[not(contains(strong, "P"))]/text()'
                )
            )
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
