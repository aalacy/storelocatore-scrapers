import csv

from concurrent import futures
from lxml import html
from sgrequests import SgRequests
from sgzip.static import static_coordinate_list, SearchableCountries


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


def get_data(url):
    rows = []
    s = set()
    locator_domain = "https://tommy.com/"

    session = SgRequests()
    r = session.get(url)
    js = r.json()["data"]

    for j in js:
        states = {"NL", "PE", "NS", "NB", "QC", "ON", "MB", "SK", "AB", "BC"}
        source = j.get("html").get("store_block")
        tree = html.fromstring(source)

        location_name = tree.xpath("//h3/text()")[0].strip()
        t = j.get("title").replace(", ,", ",").split(",")
        store_number = t[0].strip()

        street_address = ",".join(t[2:-2]).strip()
        if len(t) == 4:
            street_address = t[-3].strip()
        elif len(t) == 5:
            if t[1].strip()[0].isdigit():
                street_address = ",".join(t[1:-2]).strip()

        city = t[-2].strip()
        state = t[-1].strip()
        postal = "<MISSING>"
        if state in states:
            country_code = "CA"
        else:
            country_code = "US"
        if len(state) > 2:
            continue
        phone = (
            tree.xpath("//p[@class='store-address__info body-copy']/text()")[-1].strip()
            or "<MISSING>"
        )
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        li = tree.xpath("//li")

        for l in li:
            day = "".join(l.xpath("./span/text()")).strip()
            time = "".join(l.xpath("./p/text()")).strip()
            _tmp.append(f"{day} {time}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        page_url = "<MISSING>"

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

        if street_address not in s:
            s.add(street_address)
            rows.append(row)

    return rows


def fetch_data():
    out = []
    urls = []
    postals = []
    s = set()

    postals += static_coordinate_list(radius=200, country_code=SearchableCountries.USA)
    postals += static_coordinate_list(
        radius=200, country_code=SearchableCountries.CANADA
    )
    for p in postals:
        lat, lng = p
        urls.append(
            f"https://global.tommy.com/en_int/api/store_finder?lat={lat}&lng={lng}&radius=200&limit=-1"
        )

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                t = tuple(row[-3:-1])
                if t not in s:
                    s.add(t)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
