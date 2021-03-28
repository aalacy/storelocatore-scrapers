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
    locator_domain = "https://samandlouiespizza.com"
    api_url = "https://samandlouiespizza.com/locations/"
    session = SgRequests()

    r = session.get(api_url)
    tree = html.fromstring(r.text)
    block = tree.xpath("//div[./h3]")
    for b in block:
        slug = "".join(b.xpath('.//a[contains(text(), "View")]/@href'))
        page_url = f"{locator_domain}{slug}"

        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//div[contains(@class, 'cta')]/h1/text()"))
        line = tree.xpath('//p[@class="info-address"]/text()')
        street_address = "".join(line[0])
        a = "".join(line[1])
        city = a.split(",")[0].strip()
        state = a.split(",")[1].split()[0].strip()
        country_code = "US"
        postal = a.split(",")[1].split()[-1].strip()
        store_number = "<MISSING>"
        text = "".join(tree.xpath('//a[@class="button info-directions"]/@href'))
        try:
            latitude = text.split("/@")[1].split(",")[0]
            longitude = text.split("/@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = tree.xpath('//p[@class="info-hours"]/text()')
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation)
        phone = "".join(tree.xpath('//p[@class="info-phone"]/text()'))

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
