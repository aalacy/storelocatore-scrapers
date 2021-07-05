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

    locator_domain = "https://www.odwlogistics.com"
    api_url = "https://www.odwlogistics.com/locations-and-reach"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[text()="Learn More"]')
    for d in div:

        page_url = "https://www.odwlogistics.com" + "".join(d.xpath(".//@href"))

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath('//h2[@class="hero__title title"]/text()'))

        location_type = "".join(
            tree.xpath('//ul[@class="location__specs"]/li[1]/text()')
        ).strip()
        street_address = (
            "".join(tree.xpath('//ul[@class="location__specs"]/li[4]/text()'))
            or "<MISSING>"
        )
        if street_address == "<MISSING>":
            street_address = "".join(
                tree.xpath('//ul[@class="location__specs"]/li[2]/text()')
            )
        city_state = location_name
        if city_state.find("|") != -1:
            city_state = city_state.split("|")[0].strip()

        state = city_state.split(",")[1].strip()
        postal = "<MISSING>"
        country_code = "USA"
        city = city_state.split(",")[0].strip()
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        phone = "".join(
            tree.xpath(
                '//ul[@class="location__specs"]//a[contains(@href, "tel")]/text()'
            )
        )
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
