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

    locator_domain = "https://www.afnb.com/"
    page_url = "https://www.afnb.com/about-us/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="sf_cols"]')
    for d in div:

        phone = (
            "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
            .replace("TEL:", "")
            .strip()
        )
        street_address = (
            "".join(d.xpath(".//h3/following-sibling::p[1]/text()[1]"))
            .replace(",", "")
            .strip()
        )
        ad = (
            "".join(d.xpath(".//h3/following-sibling::p[1]/text()[2]"))
            .replace("\n", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "USA"
        city = ad.split(",")[0].strip()
        location_name = "".join(d.xpath(".//h3/text()"))
        location_type = "<MISSING>"
        if "Branch" in location_name:
            location_type = "Branch"
        if "Office" in location_name:
            location_type = "Office"
        store_number = "<MISSING>"
        latitude, longitude = "<MISSING>", "<MISSING>"
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/h4[text()="Lobby"]/following-sibling::table[1]//tr/td//text()'
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
