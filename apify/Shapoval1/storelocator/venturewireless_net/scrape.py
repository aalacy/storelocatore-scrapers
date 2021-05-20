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

    locator_domain = "https://www.venturewireless.net"
    page_url = "https://www.venturewireless.net/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./p[@style="font-size:24px"]]')

    for d in div:

        location_name = "".join(d.xpath(".//p[1]//text()"))
        location_type = "<MISSING>"
        street_address = "".join(d.xpath(".//p[3]//text()[1]"))
        ad = (
            "".join(d.xpath(".//p[3]//text()[2]")).replace("\n", "").strip()
            or "<MISSING>"
        )
        if ad == "<MISSING>":
            ad = "".join(d.xpath(".//p[4]//text()")).replace("\n", "").strip()
        phone = "".join(d.xpath(".//p[4]//text()")).replace("\n", "").strip()
        if phone.count("-") != 2:
            phone = "".join(d.xpath(".//p[5]//text()")).replace("\n", "").strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/p[.//span[contains(text(), "Hours")]]/following-sibling::p//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(d.xpath('.//p[.//span[contains(text(), "Hours")]]//text()'))
                .replace("\n", "")
                .replace("Hours:", "")
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
