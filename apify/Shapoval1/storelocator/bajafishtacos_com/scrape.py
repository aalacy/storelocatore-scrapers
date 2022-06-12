import csv
from lxml import html
from sgrequests import SgRequests
from concurrent import futures


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
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get("http://bajafishtacos.com/locations/", headers=headers)
    tree = html.fromstring(r.text)
    return tree.xpath('//a[text()="View location"]/@href')


def get_data(url):
    locator_domain = "http://bajafishtacos.com"
    page_url = url
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = (
        "".join(tree.xpath('//h2[@class="headline__secondary"]//text()'))
        .replace("\n", "")
        .strip()
    )
    street_address = (
        "".join(tree.xpath('//h3[text()="Address"]/following-sibling::p/text()[1]'))
        .replace(",", "")
        .strip()
    )
    ad = (
        "".join(tree.xpath('//h3[text()="Address"]/following-sibling::p/text()[2]'))
        .replace("\n", "")
        .replace(",", "")
        .strip()
    )
    city = " ".join(ad.split()[:-2]).strip()
    state = ad.split()[-2].strip()
    postal = ad.split()[-1].strip()
    country_code = "US"
    store_number = "<MISSING>"
    phone = "".join(tree.xpath('//h1[@class="headline__primary"]/text()'))
    location_type = "Baja Fish Tacos"
    hours_of_operation = (
        " ".join(tree.xpath('//h3[text()="Hours"]/following-sibling::p/text()'))
        .replace("\n", "")
        .strip()
    )
    text = "".join(tree.xpath("//a[contains(@href, 'maps')]/@href"))
    try:
        if text.find("ll=") != -1:
            latitude = text.split("ll=")[1].split(",")[0]
            longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = text.split("@")[1].split(",")[0]
            longitude = text.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

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
    scrape()
