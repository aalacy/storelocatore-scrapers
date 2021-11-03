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
    locator_domain = "https://www.shopdanssupermarket.com/"
    api_url = "https://www.shopdanssupermarket.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[contains(text(), "View store details")]')

    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//header/h1/text()"))

        street_address = (
            "".join(tree.xpath("//address/text()[1]")).replace("\n", "").strip()
        )
        ad = "".join(tree.xpath("//address/text()[2]")).replace("\n", "").strip()
        city = ad.split(",")[0].strip()
        state = ad.split(",")[1].strip()
        country_code = "US"
        postal = "".join(tree.xpath("//address/text()[3]")).replace("\n", "").strip()
        store_number = "<MISSING>"
        latitude = "".join(tree.xpath('//div[@class="map "]/@data-latitude'))
        longitude = "".join(tree.xpath('//div[@class="map "]/@data-longitude'))
        location_type = "Dans Supermarket"
        hours_of_operation = tree.xpath("//table//tbody/tr/td/text()")
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation)
        phone = "".join(
            tree.xpath(
                '//b[contains(text(), "Main Contact")]/following-sibling::a/text()'
            )
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
