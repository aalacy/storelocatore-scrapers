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

    locator_domain = "https://brewsters.ca"
    api_url = "https://brewsters.ca/find-us/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//li[@class="location-dets"]/p/a')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1/text()"))
        location_type = "restaurants"
        street_address = (
            "".join(
                tree.xpath(
                    '//h5[contains(text(), "Address")]/following-sibling::p[1]/text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(
                tree.xpath(
                    '//h5[contains(text(), "Address")]/following-sibling::p[1]/text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        phone = (
            "".join(
                tree.xpath(
                    '//strong[contains(text(), "Phone")]/following-sibling::a[1]/text()'
                )
            )
            .replace("BREW ", "")
            .replace("HOPS ", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip() or "<MISSING>"
        postal = " ".join(ad.split(",")[1].split()[1:]).strip() or "<MISSING>"
        country_code = "CA"
        city = ad.split(",")[0].strip() or "<MISSING>"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h5[contains(text(), "Hours of")]/following-sibling::p//text()[position()>1]'
                )
            )
            .replace("\r\n", "")
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
