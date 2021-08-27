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

    locator_domain = "https://tapandbarrel.com"
    api_url = "https://tapandbarrel.com/contact/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//h2[text()="Our Other Brands"]/preceding-sibling::div[./h3]')

    for d in div:
        page_url = "".join(d.xpath(".//h3/a/@href"))
        location_name = "".join(d.xpath(".//h3/a/text()"))
        location_type = "<MISSING>"
        street_address = "".join(
            d.xpath('.//p[@class="text-center text-sm-left"]/text()[1]')
        )
        slug = street_address
        if slug.find("-") != -1:
            slug = slug.split("-")[1].strip()
        ad = (
            "".join(d.xpath('.//p[@class="text-center text-sm-left"]/text()[2]'))
            .replace("\n", "")
            .strip()
        )
        state = "BC"
        postal = ad.split(",")[1].strip()
        country_code = "CA"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        text = "".join(d.xpath('.//a[contains(@href,"maps")]/@href'))

        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]//p//text()'))
        if location_name.find("Convention Centre") != -1:
            latitude, longitude = "<MISSING>", "<MISSING>"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        hours_of_operation = (
            " ".join(
                tree.xpath(
                    f'//p[./strong[contains(text(), "{slug}")]]/following-sibling::p[2]//text()'
                )
            )
            .replace("\n", "")
            .replace("Hours", "")
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
