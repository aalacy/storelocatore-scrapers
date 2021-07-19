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
    api = f"https://ws.bullseyelocations.com/RestSearch.svc/DoSearch2?FillAttr=true&GetHoursForUpcomingWeek=true&Radius=100&StartIndex=0&PageSize=50&Latitude={lat}&Longitude={lng}&CountryId=1&InterfaceID=15703&ClientId=5965&ApiKey=e722b82b-de25-4ceb-b09f-aab90c59d4b6"
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

    session = SgRequests()
    r = session.get(api, headers=headers)
    js = r.json()["ResultList"]

    for j in js:
        location_name = j.get("Name")
        page_url = j.get("URL")

        street_address = f'{j.get("Address1")} {j.get("Address2") or ""}'.strip()
        city = j.get("City") or "<MISSING>"
        state = j.get("State") or "<MISSING>"
        postal = j.get("PostCode") or "<MISSING>"
        country_code = "US"
        store_number = j.get("ThirdPartyId") or "<MISSING>"
        phone = j.get("PhoneNumber") or "<MISSING>"
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        location_type = j.get("LocationTypeName") or "<MISSING>"

        _tmp = []
        hours = j.get("DailyHoursList") or []
        for h in hours:
            day = h.get("NameOfDay")
            time = h.get("HoursDisplayText")
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
