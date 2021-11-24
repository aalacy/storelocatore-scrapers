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
    locator_domain = "https://www.vanzeelands.com/"
    api_url = "https://www.vanzeelands.com/Locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="loclisting type0"]')

    for d in div:

        page_url = "".join(d.xpath('.//a[contains(text(), "Location Details")]/@href'))
        location_name = "".join(d.xpath('.//div[@class="locationInfo"]/strong/text()'))
        ad = d.xpath('.//div[@class="locationInfo"]/strong/following-sibling::text()')
        ad = list(filter(None, [a.strip() for a in ad]))
        street_address = "".join(ad[0])
        csz = "".join(ad[1])
        city = csz.split(",")[0].strip()
        state = csz.split(",")[1].split()[0].strip()
        country_code = "US"
        postal = csz.split(",")[1].split()[1].strip()
        store_number = "<MISSING>"
        latitude = "".join(d.xpath('.//span[@class="hideDistance distance"]/@lat'))
        longitude = "".join(d.xpath('.//span[@class="hideDistance distance"]/@lon'))
        location_type = "Auto Care Centers"
        hours_of_operation = d.xpath(
            './/strong[contains(text(), "Hours")]/following-sibling::text() | .//strong[contains(text(), "Hours")]/following-sibling::span/text()'
        )
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation)
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))

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
