import csv
import json
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
    r = session.get(
        "https://familiprix-production.s3.amazonaws.com/sitemaps/pharmacies_sitemap.xml"
    )
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc[contains(text(), 'en/pharmacies')]/text()")


def get_data(url):
    locator_domain = "https://www.familiprix.com/en/"
    page_url = url
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    block = (
        "["
        + "".join(
            tree.xpath('//script[contains(text(), "openingHoursSpecification")]/text()')
        )
        + "]"
    )
    try:
        js = json.loads(block)
    except json.decoder.JSONDecodeError:
        return
    for j in js:
        ad = j.get("address")
        street_address = ad.get("streetAddress")
        city = ad.get("addressLocality")
        state = ad.get("addressRegion")
        postal = ad.get("postalCode")
        country_code = ad.get("addressCountry")
        store_number = "<MISSING>"
        location_name = j.get("name")
        phone = j.get("telephone")
        latitude = j.get("geo").get("latitude")
        longitude = j.get("geo").get("longitude")
        location_type = "<MISSING>"
        hours = j.get("openingHoursSpecification")
        tmp = []
        for h in hours:
            days = "".join(h.get("dayOfWeek")).split("/")[-1]
            opens = h.get("opens")
            closes = h.get("closes")
            line = f"{days} - {opens} : {closes}"
            if opens == closes:
                line = f"{days} - Closed"
            tmp.append(line)
        hours_of_operation = ";".join(tmp) or "<MISSING>"

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
