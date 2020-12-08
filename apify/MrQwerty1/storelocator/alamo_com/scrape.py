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
    urls = []
    countries = ["US", "CA"]
    session = SgRequests()

    for country in countries:
        u = (
            f"https://www.alamo.com/content/data/apis/static/common/states.sfx.json/"
            f"channelName%3Dalamo/locale%3Den_US/country={country}.json"
        )
        r = session.get(u)
        js = r.json()["statesProvinces"]
        states = js.keys()
        for state in states:
            url = (
                f"https://www.alamo.com/en_US/car-rental/locations/location-results.html"
                f"/country={country}/state={state}.html"
            )
            urls.append(url)

    return urls


def get_data(url):
    rows = []
    locator_domain = "https://www.alamo.com/"

    session = SgRequests()
    r = session.get(url)
    tree = html.fromstring(r.text)
    tr = tree.xpath("//tr[@class='row']")

    for t in tr:
        location_name = "".join(t.xpath(".//h2/text()"))

        adr = t.xpath(".//a[@class='location-address-link']/span/text()")[:-1]
        if len(adr) == 1:
            street_address = "".join(adr).strip()
        else:
            for a in adr:
                if a[0].isdigit():
                    street_address = a
                    break
            else:
                street_address = ", ".join(adr)
        line = t.xpath(".//a[@class='location-address-link']/span/text()")[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].replace("Canada", "").replace("US", "").strip()
        state = line[:2].strip()
        postal = line[2:].strip()
        country_code = url.split("country=")[1].split("/")[0]
        page_url = "https://www.alamo.com" + "".join(
            t.xpath(".//a[@data-station-id]/@href")
        )
        store_number = "".join(t.xpath(".//a[@data-station-id]/@data-station-id"))
        phone = t.xpath(".//a[contains(@href, 'tel')]/text()")[0].strip() or "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"

        days = t.xpath(".//dl[@class='locations-hours']/dt/text()")
        hours = t.xpath(".//dl[@class='locations-hours']/dd/text()")
        _tmp = []

        for d, h in zip(days, hours):
            _tmp.append(f"{d} {h}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

        if hours_of_operation.count("Closed") >= 3:
            hours_of_operation = "Closed"

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

        rows.append(row)

    return rows


def fetch_data():
    out = []
    s = set()
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                _id = row[8]  # store_number
                if _id in s:
                    continue

                s.add(_id)
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
