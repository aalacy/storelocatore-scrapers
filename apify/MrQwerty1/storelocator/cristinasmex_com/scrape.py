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
    locator_domain = "https://cristinasmex.com"
    api_url = "https://cristinasmex.com/locations/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='col-md-3 col-sm-6 info contact-padding']")

    _tmp = []
    days = tree.xpath(
        "//h3[contains(text(), 'Hours')]/following-sibling::ul[@style='list-style-type: none; line-height: .5rem; padding-left: 0px;']/li[contains(@style, 'white')]/p/text()"
    )
    times = tree.xpath(
        "//h3[contains(text(), 'Hours')]/following-sibling::ul[@style='list-style-type: none; line-height: .5rem; padding-left: 0px;']/li[contains(@style, '#dfa')]/p/text()"
    )[1:]

    for d, t in zip(days, times):
        _tmp.append(f"{d.strip()}: {t.strip()}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

    for d in divs:
        location_name = "".join(d.xpath(".//h3/text()")).strip()
        line = d.xpath("./address/text()")
        line = list(filter(None, [l.strip() for l in line]))

        street_address = line[0]
        phone = line[-1]
        line = line[1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[-1]
        country_code = "US"
        store_number = "<MISSING>"
        slug = "".join(d.xpath(".//a[@class='btn-default btn']/@href")).split("#")[0]
        page_url = f"{locator_domain}{slug}"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"

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
