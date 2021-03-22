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
    locator_domain = "https://thecanadianbrewhouse.com"
    page_url = "https://thecanadianbrewhouse.com/locations/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://thecanadianbrewhouse.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    li = tree.xpath('//div[@class="col-lg-4 col-md-6 col-sm-12"]')
    for l in li:

        street_address = "".join(l.xpath('.//div[@class="wrap"]/p[1]/text()'))
        ad = "".join(l.xpath('.//div[@class="wrap"]/p[2]/text()'))
        city = ad.split(",")[0]
        postal = " ".join(ad.split(",")[1].split()[-2:])
        state = " ".join(ad.split(",")[1].split()[:-2])
        country_code = "CA"
        store_number = "<MISSING>"
        location_name = "".join(l.xpath(".//h3/text()"))
        phone = "".join(l.xpath('.//a[@class="locations-list-phone"]/text()')).strip()
        latitude = "".join(
            l.xpath(
                f'.//preceding::div[./h4[contains(text(), "{location_name}")]]/@data-lat'
            )
        )
        longitude = "".join(
            l.xpath(
                f'.//preceding::div[./h4[contains(text(), "{location_name}")]]/@data-lng'
            )
        )
        location_type = "<MISSING>"
        hours_of_operation = (
            ";".join(l.xpath('.//div[@class="card card-body"]/p[1]/text()'))
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
