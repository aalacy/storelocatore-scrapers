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


def get_coords_from_google_url(url):
    try:
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def fetch_data():
    out = []
    locator_domain = "https://www.tylerstx.com/"
    page_url = "https://www.tylerstx.com/storelocations"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[@class='shg-c-lg-3 shg-c-md-3 shg-c-sm-3 shg-c-xs-6']|//div[@class='shg-c-lg-4 shg-c-md-4 shg-c-sm-4 shg-c-xs-4']"
    )

    for d in divs:
        location_name = "".join(d.xpath(".//div[last()]/div/p[1]/span/text()"))
        line = d.xpath(".//p/a[contains(@href, 'google')]/span/text()")
        line = list(filter(None, [l.strip() for l in line]))

        street_address = line[0]
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[-1]
        country_code = "US"
        store_number = "<MISSING>"
        phone = "".join(d.xpath(".//p[last()]//text()")).strip() or "<MISSING>"
        text = "".join(d.xpath(".//p/a[contains(@href, 'google')]/@href"))
        latitude, longitude = get_coords_from_google_url(text)
        location_type = "<MISSING>"

        _tmp = []
        days = d.xpath(".//span[./span[@style='font-weight: bold;']]/span/text()")
        times = d.xpath(".//span[./span[@style='font-weight: bold;']]/text()")

        for date, t in zip(days, times):
            _tmp.append(f"{date.strip()} {t.strip()}")

        hours_of_operation = " ".join(_tmp) or "<MISSING>"

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
