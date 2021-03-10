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


def get_data(coord):
    rows = []
    lat, lon = coord
    locator_domain = "https://www.walkaboutbars.co.uk/"
    api_url = "https://www.walkaboutbars.co.uk/heremapscurrent"
    data = {"latitude": lat, "longitude": lon}

    session = SgRequests()
    r = session.post(api_url, data=data)
    js = r.json().get("mapPoints") or []

    for j in js:
        location_name = j.get("UnitName")
        street_address = (
            f'{j.get("Address1")} {j.get("Address2") or ""}'.strip() or "<MISSING>"
        )
        city = j.get("TownCity") or "<MISSING>"
        state = j.get("County") or "<MISSING>"
        postal = j.get("PostCode") or "<MISSING>"
        country_code = "GB"
        store_number = j.get("id") or "<MISSING>"
        phone = j.get("Telephone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        page_url = f'https://www.walkaboutbars.co.uk/{j.get("UrlText")}'
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
        rows.append(row)

    return rows


def get_hours(row):
    _tmp = []
    session = SgRequests()
    url = row[1]
    r = session.get(url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='opening-times']/div[./span]")
    for d in divs:
        day = "".join(d.xpath("./span/text()")).strip()
        time = "".join(d.xpath("./text()")).strip()
        _tmp.append(f"{day} {time}")

    hours = ";".join(_tmp) or "<MISSING>"
    if hours.lower().count("closed") == 7:
        hours = "Closed"
    row[-1] = hours
    return row


def fetch_data():
    out = []
    inputs = []
    s = set()
    coords = static_coordinate_list(
        radius=200, country_code=SearchableCountries.BRITAIN
    )

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, coord): coord for coord in coords}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                _id = row[8]
                if _id not in s:
                    s.add(_id)
                    inputs.append(row)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_hours, inp): inp for inp in inputs}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
