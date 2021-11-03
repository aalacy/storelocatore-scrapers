import csv
from lxml import html
from concurrent import futures
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
    lat, lng = coord
    locator_domain = "https://www.quantumvisioncenters.com"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    session = SgRequests()

    r = session.get(
        f"https://www.quantumvisioncenters.com/wp-json/352inc/v1/locations/coordinates?lat={lat}&lng={lng}",
        headers=headers,
    )
    js = r.json()

    for j in js:

        page_url = j.get("permalink")
        location_name = "".join(j.get("name")).replace("&#8211;", "–")
        street_address = f"{j.get('address1')} {j.get('address2')} {j.get('address3')}"
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip_code")
        country_code = "US"
        store_number = "<MISSING>"
        phone = j.get("phone_number")
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = "<MISSING>"
        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="col-lg-4 times"]/div/span//text()'))
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.count("Closed") == 7:
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
    coords = static_coordinate_list(radius=50, country_code=SearchableCountries.USA)

    with futures.ThreadPoolExecutor(max_workers=2) as executor:
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
