import csv
import json

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
    _tmp = []
    session = SgRequests()
    r = session.get(url)
    tree = html.fromstring(r.text)

    hours = tree.xpath(
        "//div[@class='location-info-right-wrapper']//table[@class='c-location-hours-details']"
        "//tr[contains(@class, 'c-location-hours-details')]"
    )
    for h in hours:
        day = "".join(h.xpath("./td[@class='c-location-hours-details-row-day']/text()"))
        time = " ".join(
            h.xpath(
                ".//span[@class='c-location-hours-details-row-intervals-instance ']//text()"
            )
        )
        if time:
            _tmp.append(f"{day} {time}")
        else:
            _tmp.append(f"{day} Closed")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

    if hours_of_operation.count("Closed") == 7:
        hours_of_operation = "Closed"

    return hours_of_operation


def fetch_data():
    out = []
    locator_domain = "https://pizzaranch.com"
    session = SgRequests()

    for i in range(1, 5000):
        urls = set()
        hours = dict()

        r = session.get(
            f"https://pizzaranch.com/all-locations/search-results/p{i}?state=*"
        )
        tree = html.fromstring(r.text)
        size = tree.xpath("//location-info-panel")
        text = "".join(
            tree.xpath("//script[contains(text(), 'var locations = ')]/text()")
        )
        text = text.split("var locations = ")[1].replace(";", "")
        js = json.loads(text)

        for j in js:
            url = j.get("website")
            if url:
                urls.add(url)

        with futures.ThreadPoolExecutor(max_workers=12) as executor:
            future_to_url = {executor.submit(get_hours, url): url for url in urls}
            for future in futures.as_completed(future_to_url):
                k = future_to_url[future].split("/")[-1]
                hours[k] = future.result()

        for j in js:
            location_name = j.get("title")
            street_address = j.get("address1")
            city = j.get("city")
            state = j.get("state")
            postal = j.get("zipCode")
            country_code = "US"
            store_number = j.get("id")
            phone = j.get("phone")
            location_type = "<MISSING>"
            latitude = j.get("lat")
            longitude = j.get("lng")
            page_url = j.get("website") or "<MISSING>"

            try:
                key = page_url.split("/")[-1]
                hours_of_operation = hours[key]
            except:
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

            out.append(row)

        if len(size) < 12:
            break

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
