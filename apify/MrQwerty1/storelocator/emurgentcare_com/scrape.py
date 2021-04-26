import csv

from concurrent import futures
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


def get_urls():
    session = SgRequests()
    r = session.get("https://www.amc.edu/emurgentcare/zipcode-finder.cfm")
    tree = html.fromstring(r.text)

    return tree.xpath("//ul[@id='contactsubnav']/div//a/@href")


def get_data(url):
    locator_domain = "https://www.amc.edu/"
    page_url = f"https://www.amc.edu/emurgentcare/{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//div[@id='locDetails']/h3/text()")).strip()
    line = tree.xpath("//div[@id='locDetails']/p/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = line.pop(0)
    city = line.pop(0)
    state = "<MISSING>"
    postal = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "".join(tree.xpath("//a[@class='phoneIcon']/text()")).strip() or "<MISSING>"

    text = "".join(tree.xpath("//a[@class='navigateIcon']/@href"))
    latitude, longitude = get_coords_from_google_url(text)
    location_type = "<MISSING>"
    hours_of_operation = (
        ";".join(tree.xpath("//div[@id='hours']//h3/text()")).strip() or "<MISSING>"
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

    return row


def fetch_data():
    out = []
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=12) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
