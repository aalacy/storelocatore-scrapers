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
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get("https://www.petro.com/petro-locations", headers=headers)

    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='addressListing']/a/@href")


print(get_urls())


def get_data(url):
    locator_domain = "https://www.petro.com"
    page_url = f"https://www.petro.com{url}"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    ad = tree.xpath('//div[@class="street"]/p/text()')
    ad = list(filter(None, [a.strip() for a in ad]))
    street_address = " ".join(ad[:-1])
    ad = ad[-1]
    if ad.count(",") == 2:
        ad = ad.replace(",", "")
    if ad.find(",") != -1:
        city = ad.split(",")[0].strip()
        ad = ad.split(",")[1].strip()
    else:
        city = " ".join(ad.split()[:-2])
        ad = ad.replace(city, "").strip()
    state = ad.split()[0]
    postal = ad.split()[1]
    country_code = "US"

    store_number = "<MISSING>"
    location_name = f"Petro Home Services {city}, {state}"
    phone = (
        "".join(tree.xpath('//p[contains(text(), "Sales")]/text()'))
        .replace("Sales:", "")
        .strip()
        or "<MISSING>"
    )
    if phone.find("\n") != -1:
        phone = phone.split("\n")[0]
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = "<MISSING>"

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
