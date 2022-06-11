import csv
import json
import re
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
        "Referer": "https://www.coastalcountry.com/about/store-locations",
        "Proxy-Authorization": "Basic YWNjZXNzX3Rva2VuOmc3NzExNnBzajZqbGZhaHM5dHJwMDdocm0ydTlxNGVzM3BhaGNrYm9oY2kzOGEzMWtpdQ==",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get("https://www.coastalcountry.com/Sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc[contains(text(), '/about/store-locations/')]/text()")


def get_data(url):
    locator_domain = "https://www.coastalcountry.com/"
    page_url = url
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.coastalcountry.com/about/store-locations",
        "Proxy-Authorization": "Basic YWNjZXNzX3Rva2VuOmc3NzExNnBzajZqbGZhaHM5dHJwMDdocm0ydTlxNGVzM3BhaGNrYm9oY2kzOGEzMWtpdQ==",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get(page_url, headers=headers)
    content = r.text.split("var serverSideViewModel =")[1].split(";")[0]
    content = "[" + content + "]"
    content = re.sub("storeId:", '"storeId":', content)
    content = re.sub("storeName:", '"storeName":', content)
    content = re.sub("addressLine1:", '"addressLine1":', content)
    content = re.sub("addressLine2:", '"addressLine2":', content)
    content = re.sub("city:", '"city":', content)
    content = re.sub("state:", '"state":', content)
    content = re.sub("zipCode:", '"zipCode":', content)
    content = re.sub("phoneNumber:", '"phoneNumber":', content)
    content = re.sub("emailAddress:", '"emailAddress":', content)
    content = re.sub("storeHours:", '"storeHours":', content)
    content = re.sub("storeFeatures:", '"storeFeatures":', content)
    content = re.sub("latitude:", '"latitude":', content)
    content = re.sub("longitude:", '"longitude":', content)
    content = re.sub("isOnlineStore:", '"isOnlineStore":', content)

    js = json.loads(content)
    for j in js:
        street_address = j.get("addressLine1")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zipCode")
        country_code = "US"
        store_number = "<MISSING>"
        location_name = j.get("storeName")
        phone = j.get("phoneNumber")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        location_type = "<MISSING>"
        hours_of_operation = "".join(j.get("storeHours")).replace("\n", " ")

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
