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


def get_urls():
    session = SgRequests()
    r = session.get(
        "https://www.renewalbyandersen.com/about/renewal-by-andersen-showrooms"
    )
    tree = html.fromstring(r.text)

    return set(
        tree.xpath(
            "//div[@class='row component column-splitter ']//a[contains(@href, 'window-company')]/@href"
        )
    )


def get_data(page_url):
    rows = []
    locator_domain = "https://www.renewalbyandersen.com/"
    store_number = page_url.split("/")[-2].split("-")[0]

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    if "retailer" in page_url:
        location_type = "Retailer"
        locations = tree.xpath(
            "//div[@class='component address-hours o-flex--column columns']"
        )
        for loc in locations:
            location_name = "".join(
                loc.xpath(".//h3[@class='hdg hdg--3 showroomheading']/text()")
            ).strip()
            line = loc.xpath(
                ".//div[@class='o-flex--column showroomaddress']/div/text()"
            )
            line = list(filter(None, [l.strip() for l in line]))
            if not line:
                continue

            street_address = ", ".join(line[:-1])
            if not street_address:
                continue

            line = line[-1]
            city = line.split(",")[0].strip()
            line = line.split(",")[1].strip()
            if line.count(" ") == 1:
                state = line.split()[0]
                postal = line.split()[1]
                country_code = "US"
            else:
                state = "<MISSING>"
                postal = line
                country_code = "CA"

            if len(postal) < 5:
                postal = line
                state = "<MISSING>"
                country_code = "CA"

            phone = (
                "".join(
                    loc.xpath(".//a[@class='txt txt--link showroomphone']/text()")
                ).strip()
                or "<MISSING>"
            )
            _map = "".join(
                tree.xpath("//map-config[@data-map-config]/@data-map-config")
            )
            if _map:
                try:
                    geo = json.loads(_map)["ShowroomLocations"][0]
                except:
                    geo = {}
                latitude = geo.get("Latitude") or "<MISSING>"
                longitude = geo.get("Longitude") or "<MISSING>"
            else:
                latitude, longitude = "<MISSING>", "<MISSING>"

            _tmp = []
            divs = loc.xpath(".//div[@class='showroom__hours-container']")
            for d in divs:
                line = " ".join("".join(d.xpath(".//text()")).split())
                if "(" in line:
                    line = line.split("(")[0].strip()
                if "closed" in line.lower():
                    line = "Closed"
                if "Call" in line:
                    continue
                _tmp.append(line)

            hours_of_operation = ";".join(_tmp) or "<MISSING>"
            if "Not Yet" in hours_of_operation:
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
            rows.append(row)

    elif "about-us" in page_url:
        location_type = "Showroom"

        showrooms = tree.xpath(
            "//div[contains(@class,'micrositeshowroom micrositeshowroom')]"
        )
        for s in showrooms:
            location_name = "".join(s.xpath(".//h2/text()")).strip()
            line = s.xpath(".//address//text()")
            line = list(filter(None, [l.strip() for l in line]))

            street_address = ", ".join(line[:-1])
            line = line[-1]
            city = line.split(",")[0].strip()
            line = line.split(",")[1].strip()
            state = line.split()[0]
            postal = line.replace(state, "").strip()
            country_code = "US"

            if len(postal) < 5:
                postal = line
                state = "<MISSING>"
                country_code = "CA"

            phone = "".join(s.xpath(".//a/text()")).strip() or "<MISSING>"
            _map = "".join(
                tree.xpath("//map-config[@data-map-config]/@data-map-config")
            )
            if _map:
                try:
                    geo = json.loads(_map)["ShowroomLocations"][0]
                except:
                    geo = {}
                latitude = geo.get("Latitude") or "<MISSING>"
                longitude = geo.get("Longitude") or "<MISSING>"
            else:
                latitude, longitude = "<MISSING>", "<MISSING>"

            _tmp = []
            divs = s.xpath(".//h3[text()='STORE HOURS']/following-sibling::ul/li")
            for d in divs:
                line = " ".join("".join(d.xpath(".//text()")).split())
                if "(" in line:
                    line = line.split("(")[0].strip()
                if "closed" in line.lower():
                    line = "Closed"
                if "Call" in line:
                    continue
                _tmp.append(line)

            hours_of_operation = ";".join(_tmp) or "<MISSING>"
            if "Not Yet" in hours_of_operation:
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
