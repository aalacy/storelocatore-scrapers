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


def get_urls():
    session = SgRequests()
    r = session.get("https://locations.ecoatm.com/")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@id='EUStatesAbbr']/@href")


def get_data(coord):
    rows = []
    lat, lng = coord
    locator_domain = "https://ecoatm.com"
    api = f"https://locations.ecoatm.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://locations.ecoatm.com/",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://locations.ecoatm.com",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    data = {"latitudeInput": lat, "longitudeInput": lng}

    session = SgRequests()
    r = session.post(api, headers=headers, data=data)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='resultsDetails']")

    for d in divs:
        location_name = "".join(d.xpath(".//h3[@itemprop='name']/a/text()")).strip()
        page_url = "https://locations.ecoatm.com/" + "".join(
            d.xpath(".//h3[@itemprop='name']/a/@href")
        )

        street_address = "".join(
            d.xpath(".//span[@itemprop='streetAddress']/text()")
        ).strip()
        city = "".join(d.xpath(".//span[@itemprop='addressLocality']/text()")).strip()
        if city.endswith(","):
            city = city[:-1].strip()
        state = "".join(d.xpath(".//span[@itemprop='addressRegion']/text()")).strip()
        postal = "".join(d.xpath(".//span[@itemprop='postalCode']/text()")).strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = "".join(d.xpath(".//span[@itemprop='telephone']/a/text()")).strip()
        latitude = (
            "".join(d.xpath(".//meta[@itemprop='latitude']/@content")).replace(",", ".")
            or "<MISSING>"
        )
        longitude = (
            "".join(d.xpath(".//meta[@itemprop='longitude']/@content")).replace(
                ",", "."
            )
            or "<MISSING>"
        )
        location_type = "<MISSING>"

        _tmp = []
        hours = d.xpath(".//div[@class='hoursItemWrap']")
        for h in hours:
            day = "".join(h.xpath(".//span[@class='dayName']/text()")).strip()
            time = "".join(h.xpath(".//span[@class='regularHours']/text()")).strip()
            _tmp.append(f"{day}: {time}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
    coords = static_coordinate_list(radius=50, country_code=SearchableCountries.USA)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, coord): coord for coord in coords}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                _id = row[1]
                if _id not in s:
                    s.add(_id)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
