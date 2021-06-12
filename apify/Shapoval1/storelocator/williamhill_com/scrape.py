import csv
from lxml import html
import json
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
    locator_domain = "https://www.williamhill.com"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }
    data = {
        "lat": f"{lat}",
        "lng": f"{lng}",
    }
    session = SgRequests()

    r = session.post(
        "https://shoplocator.williamhill/results", headers=headers, data=data
    )
    """tree = html.fromstring(r.text)
    div = tree.xpath('//div[@id="store-info"]')"""
    tree = html.fromstring(r.text)
    jsblock = "".join(
        tree.xpath('//script[contains(text(), "window.lctr.results.push(")]/text()')
    ).split("window.lctr.results.push(")[1:]
    for i in jsblock:
        i = i.replace(");", "")
        i = "[" + i + "]"
        try:
            js = json.loads(i)
        except:
            continue
        for j in js:
            slug = "".join(j.get("slug"))
            page_url = f"{locator_domain}{slug}"
            location_name = j.get("name") or "<MISSING>"
            street_address = (
                f"{j.get('street_no')} {j.get('street')}".replace("None", "").strip()
                or "<MISSING>"
            )
            if j.get("city"):
                city = j.get("city")
            else:
                city = j.get("country")
            if city:
                city = city
            else:
                city = "<MISSING>"
            state = "<MISSING>"
            postal = j.get("post_code") or "<MISSING>"
            country_code = "GB"
            store_number = j.get("location_id") or "<MISSING>"
            phone = j.get("phone") or "<MISSING>"
            latitude = j.get("latitude") or "<MISSING>"
            longitude = j.get("longitude") or "<MISSING>"
            location_type = "<MISSING>"
            try:
                hours_of_operation = f"Monday {j.get('mon_open')} - {j.get('mon_close')} Tuesday {j.get('tue_open')} - {j.get('tue_close')} Wednesday {j.get('wed_open')} - {j.get('wed_close')} Thursday {j.get('thu_open')} - {j.get('thu_close')} Friday {j.get('fri_open')} - {j.get('fri_close')} Saturday {j.get('sat_open')} - {j.get('sat_close')} Sunday {j.get('sun_open')} - {j.get('sun_close')}"
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
            rows.append(row)

    return rows


def fetch_data():
    out = []
    s = set()
    coords = static_coordinate_list(radius=1, country_code=SearchableCountries.BRITAIN)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, coord): coord for coord in coords}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                _id = row[3]
                if _id not in s:
                    s.add(_id)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
