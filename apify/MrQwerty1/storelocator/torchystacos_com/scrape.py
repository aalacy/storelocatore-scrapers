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


def get_hours(url):
    _id = url.split("/")[-2]
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }
    r = session.get(url, proxies=proxies, headers=headers)
    tree = html.fromstring(r.text)
    hoo = (
        ";".join(
            tree.xpath("//div[@class='show-more']/p[@itemprop='openingHours']/text()")
        )
        or "<MISSING>"
    )

    return {_id: hoo}


def fetch_data():
    out = []
    urls = []
    hours = []
    session = SgRequests()
    locator_domain = "https://torchystacos.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    r = session.get(
        "https://torchystacos.com/locations-json/", proxies=proxies, headers=headers
    )
    js = r.json()

    for j in js:
        urls.append("https://torchystacos.com" + j.get("permalink"))

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_hours, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            hours.append(future.result())

    hours = {k: v for elem in hours for (k, v) in elem.items()}

    for j in js:
        page_url = "https://torchystacos.com" + j.get("permalink")
        _id = page_url.split("/")[-2]
        location_name = j.get("name")
        street_address = j.get("address") or "<MISSING>"
        if street_address.find("77005") != -1:
            street_address = street_address.split(",")[0]
        city = j.get("city") or "<MISSING>"
        state = j.get("state_abbr") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("id") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"

        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lon") or "<MISSING>"
        location_type = "<MISSING>"

        if location_name.lower().find("coming") == -1:
            hours_of_operation = hours.get(_id)
        else:
            hours_of_operation = "Coming Soon"

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
    proxies = {"https": "http://MrKrabs:rfrfirf123@us-ny.proxymesh.com:31280"}
    scrape()
