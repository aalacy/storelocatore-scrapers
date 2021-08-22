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

    locator_domain = "https://www.localfoodstexas.com"
    api_url = "https://www.localfoodstexas.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="col-md-6"]')

    for d in div:
        slug = "".join(d.xpath('.//a[contains(@href, "location/")]/@href'))
        location_name = "".join(d.xpath(".//h2[1]/text()"))

        page_url = f"{locator_domain}{slug}"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        street_address = (
            "".join(
                tree.xpath(
                    '//p/a[contains(@data-bb-track-category, "Address")]/text()[1]'
                )
            )
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )
        ad = (
            "".join(
                tree.xpath(
                    '//p/a[contains(@data-bb-track-category, "Address")]/text()[2]'
                )
            )
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )
        phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()')) or "<MISSING>"
        state = ad.split()[1].strip()
        postal = ad.split()[2].strip()
        country_code = "US"
        city = ad.split()[0]
        store_number = "<MISSING>"
        ll = "".join(tree.xpath('//div[@class="gmaps"]/@data-gmaps-static-url-mobile'))
        latitude = ll.split("center=")[1].split("%2C")[0]
        longitude = ll.split("center=")[1].split("%2C")[1].split("&")[0]
        hours_of_operation = "".join(tree.xpath('//div[@class="col-md-6"]/p[2]/text()'))
        if hours_of_operation.find("Our") != -1:
            hours_of_operation = hours_of_operation.split("Our")[0].strip()
        location_type = "Local Foods"
        cms = "".join(tree.xpath('//p[contains(text(), "Coming Soon!")]/text()'))
        if cms:
            hours_of_operation = "Coming Soon"
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
