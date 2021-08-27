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


def get_urls():
    r = session.get("https://stores.kohler.com/en/locations/experience-centers")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='ksslocationcards--store-link']/@href")


def get_data(url):
    locator_domain = "https://stores.kohler.com/en/locations/experience-centers"
    page_url = f"https://stores.kohler.com{url}"

    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//input[@id='Location']/@value"))
    street_address = "".join(tree.xpath("//input[@id='Address']/@value"))
    city = "".join(tree.xpath("//input[@id='City']/@value"))
    state = "".join(tree.xpath("//input[@id='State']/@value"))
    postal = "".join(tree.xpath("//input[@id='Zip']/@value"))
    country_code = "US"
    store_number = "".join(tree.xpath("//input[@id='bpnumber']/@value")[0])
    phone = "".join(tree.xpath("//input[@id='Phone']/@value"))
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    hours = tree.xpath("//div[@class='opening-time']/input")

    for h in hours:
        day = "".join(h.xpath("./@data-day"))
        time = "".join(h.xpath("./@data-time"))
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

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

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
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
    session = SgRequests()
    scrape()
