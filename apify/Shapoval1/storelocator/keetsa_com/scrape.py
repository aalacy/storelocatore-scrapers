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

    locator_domain = "https://www.keetsa.com"
    api_url = "https://www.keetsa.com/pages/mattress-stores"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[@class="gf_column gf_col-lg-6 gf_col-md-6 gf_col-xs-12 gf_col-sm-12"]'
    )
    for d in div:

        page_url = locator_domain + "".join(
            d.xpath('.//a[./span[text()="See Details"]]/@href')
        )

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(
            tree.xpath('//font[text()="PHONE"]/preceding::h2[1]//text()')
        )
        ad = "".join(
            tree.xpath(
                '//font[text()="PHONE"]/preceding::a[contains(@href, "maps")][1]//text()'
            )
        )

        location_type = "<MISSING>"
        street_address = ad.split(",")[0].strip()
        state = ad.split(",")[2].split()[0].strip()
        postal = ad.split(",")[2].split()[1].strip()
        country_code = "USA"
        city = ad.split(",")[1].strip()
        store_number = "<MISSING>"
        text = "".join(
            tree.xpath(
                '//font[text()="PHONE"]/preceding::a[contains(@href, "maps")][1]/@href'
            )
        )
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = (
            " ".join(
                tree.xpath(
                    '//p[./b/font[text()="PHONE"]]/following-sibling::p[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//p[./font/b[text()="HOURS"]]/following-sibling::p//text() | //b[text()="HOURS"]/following-sibling::span/text()'
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
