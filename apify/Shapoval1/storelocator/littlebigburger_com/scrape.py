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

    locator_domain = "https://littlebigburger.com"

    api_url = "https://littlebigburger.com/locations-menus/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath('//a[contains(@href, "locations/")]')
    for b in block:

        slug = "".join(b.xpath(".//@href"))
        page_url = f"{locator_domain}{slug}"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = "".join(tree.xpath("//h4//text()")).strip()
        location_type = "<MISSING>"
        street_address = "".join(tree.xpath("//h3/span[1]/text()"))
        ll = "".join(
            tree.xpath(
                '//div[@class="et_pb_module et_pb_code et_pb_code_0"]//*[contains(@data-center, "-")]/@data-center'
            )
        )
        latitude = ll.split(",")[1]
        longitude = ll.split(",")[0]
        country_code = "US"
        state = "".join(tree.xpath("//h3/span[3]/text()"))
        if page_url.find("/capitolhill/") != -1:
            state = "".join(tree.xpath("//h3/span[2]/span/text()"))
        state = state.replace("regon", "Oregon").replace(",", "").strip()
        if state == "orth Carolina":
            state = state.replace("orth Carolina", "North Carolina")
        postal = "".join(tree.xpath("//h3/span[4]/text()"))
        city = "".join(tree.xpath("//h3/span[2]/text()")).replace(",", "")
        store_number = "<MISSING>"
        hours_of_operation = (
            "".join(tree.xpath('//h3[contains(text(), "Mon")]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()')) or "<MISSING>"

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
