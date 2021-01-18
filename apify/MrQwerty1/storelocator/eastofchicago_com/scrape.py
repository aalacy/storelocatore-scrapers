import csv

from concurrent import futures
from lxml import html
from sgrequests import SgRequests
from sgzip.static import static_zipcode_list, SearchableCountries


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


def get_data(z):
    out = []
    url = "https://www.eastofchicago.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0"
    }

    api_url = f"https://www.bullseyelocations.com/pages/Location-nomap?CountryId=1&radius=100&Zip={z}"
    r = session.get(api_url, headers=headers)

    tree = html.fromstring(r.text)
    li = tree.xpath("//ul[@id='resultsCarouselWide']/li")
    for l in li:
        locator_domain = url
        location_name = "".join(l.xpath(".//h3[@itemprop='name']/text()")).strip()
        page_url = "".join(l.xpath(".//a[@id='website']/@href")) or "<MISSING>"
        if page_url.startswith("//"):
            page_url = f"https:{page_url}"
        street_address = "".join(
            l.xpath(".//span[@itemprop='streetAddress']/text()")
        ).strip()
        city = (
            "".join(l.xpath(".//span[@itemprop='addressLocality']/text()")).strip()[:-1]
            or "<MISSING>"
        )
        state = (
            "".join(l.xpath(".//span[@itemprop='addressRegion']/text()")).strip()
            or "<MISSING>"
        )
        postal = (
            "".join(l.xpath(".//span[@itemprop='postalCode']/text()")).strip()
            or "<MISSING>"
        )
        country_code = "US"
        store_number = (
            "".join(l.xpath(".//input[@id='ThirdPartyId']/@value")) or "<MISSING>"
        )
        try:
            phone = l.xpath(".//span[@itemprop='telephone']/text()")[0].strip()
        except IndexError:
            phone = "<MISSING>"
        latitude = (
            "".join(l.xpath(".//meta[@itemprop='latitude']/@content")) or "<MISSING>"
        )
        longitude = (
            "".join(l.xpath(".//meta[@itemprop='longitude']/@content")) or "<MISSING>"
        )
        if latitude == "0" or longitude == "0":
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            "".join(l.xpath(".//div[@class='popDetailsHours']/meta/@content")).replace(
                "|", ";"
            )[:-1]
            or "<MISSING>"
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


def fetch_data():
    out = []
    s = set()
    zips = static_zipcode_list(radius=100, country_code=SearchableCountries.USA)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, z): z for z in zips}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                if row:
                    check = tuple(row[2:6])
                    if check not in s:
                        s.add(check)
                        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
