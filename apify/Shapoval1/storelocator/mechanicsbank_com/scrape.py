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
    locator_domain = "https://www.wetzels.com"
    lat, lng = coord
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    session = SgRequests()

    r = session.get(
        f"https://mobileapi.locatorsearch.com/LocatorSearchAPI.asmx/FindLocations?UserName=B907AC7F&Password=B907AC7F-D0D6-4A6A-8247-0CC0DF510621&AddressLine=&City=&State=&PostalCode=&Country=&Latitude={lat}&Longitude={lng}&Type=FCS&Offset=100",
        headers=headers,
    )
    tree = html.fromstring(r.content)
    div = tree.xpath("//location")

    for d in div:

        page_url = "https://www.mechanicsbank.com/locations"
        location_name = (
            "".join(d.xpath('.//attribute[@key="LocationName"]/text()')) or "<MISSING>"
        )
        street_address = (
            "".join(d.xpath('.//attribute[@key="AddressLine"]/text()')) or "<MISSING>"
        )
        city = "".join(d.xpath('.//attribute[@key="CityName"]/text()')) or "<MISSING>"
        state = "".join(d.xpath('.//attribute[@key="StateCode"]/text()')) or "<MISSING>"
        postal = (
            "".join(d.xpath('.//attribute[@key="PostalCode"]/text()')) or "<MISSING>"
        )
        country_code = (
            "".join(d.xpath('.//attribute[@key="CountryCode"]/text()')) or "<MISSING>"
        )
        store_number = "<MISSING>"
        phone = "".join(d.xpath('.//attribute[@key="Phone"]/text()')) or "<MISSING>"
        latitude = (
            "".join(d.xpath('.//attribute[@key="Latitude"]/text()')) or "<MISSING>"
        )
        longitude = (
            "".join(d.xpath('.//attribute[@key="Longitude"]/text()')) or "<MISSING>"
        )
        location_type = (
            "".join(d.xpath('.//attribute[@key="LocationTypeLabel"]/text()'))
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(d.xpath('.//attribute[@key="AdditionalDetails2"]/text()'))
            or "<MISSING>"
        )
        if hours_of_operation.find("Hours") != -1:
            hours_of_operation = (
                hours_of_operation.split("Hours:")[1].split("Services")[0].strip()
            )
        hours_of_operation = (
            hours_of_operation.replace("pmClosed", "pm Closed")
            .replace("pmFriday", "pm Friday")
            .replace("pmSaturday", "pm Saturday")
        )

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
    coords = static_coordinate_list(radius=100, country_code=SearchableCountries.USA)

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
