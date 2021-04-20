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

    locator_domain = "https://www.tcwri.org"
    api_url = "https://www.tcwri.org/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath(
        '//a[./div/div/div/p[contains(text(), "Locations")]]/following-sibling::ul/li/a'
    )
    for b in block:

        page_url = "".join(b.xpath(".//@href"))
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1/text()"))
        adr = "".join(
            tree.xpath(
                '//div[.//h1]/following-sibling::div//p/text() | //div[.//h1]/following-sibling::div//span[@class="color_24"]/text()'
            )
        )
        location_type = "<MISSING>"
        street_address = adr.split(",")[0].strip()
        phone = "".join(
            tree.xpath('//h6[.//span[contains(text(), "Call the")]]/a/@href')
        ).replace("tel:", "")
        state = adr.split(",")[2].split()[0]
        postal = adr.split(",")[2].split()[-1]
        country_code = "USA"
        city = adr.split(",")[1].strip()
        store_number = "<MISSING>"
        text = "".join(
            tree.xpath('//h6[.//span[contains(text(), "Locate Us")]]/a/@href')
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
        hours_of_operation = "".join(
            tree.xpath('//span[contains(text(), "open from")]/text()')
        )
        if hours_of_operation.find("open from") != -1:
            hours_of_operation = (
                hours_of_operation.split("open from")[1].split("and tuition")[0].strip()
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
