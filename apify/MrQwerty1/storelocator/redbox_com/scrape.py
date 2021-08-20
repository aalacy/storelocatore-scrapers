import csv
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
    session = SgRequests()

    locator_domain = "https://www.redbox.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "*/*",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.redbox.com/locations",
        "content-type": "application/json",
        "x-redbox-device-type": "RedboxWebWindows",
        "Origin": "https://www.redbox.com",
        "Connection": "keep-alive",
        "TE": "Trailers",
    }

    data = {
        "operationName": "getStores",
        "variables": {
            "latitude": float(lat),
            "longitude": float(lng),
            "productId": "",
            "getInventory": False,
            "getProximity": False,
            "numResults": 20,
        },
        "query": "query getStores($latitude: Decimal!, $longitude: Decimal!, $productId: String, $getInventory: Boolean!, $numResults: Int!, $getProximity: Boolean!) {  nearbyStores(filter: {latitude: $latitude, longitude: $longitude, radiusMiles: 10, productId: $productId}, paging: {number: 0, size: $numResults}) {    store {      id      hideTax      online      profile {        name        location {          address          city          isIndoor          latitude          longitude          state          zip          __typename        }        vendor        hasKeypad        canSellMovies        __typename      }      inventory @include(if: $getInventory) {        physicalTitleId        rental        purchase        stock: inStock        defRental        extra        deal: isDeal        isThinned        salePrice        mnp: multiNightPricing {          id          night          price          extraNight          __typename        }        product {          name          __typename        }        __typename      }      __typename    }    proximity @include(if: $getProximity) {      latitude      longitude      dist: distanceMiles      drv: drivingInstructionsAvailable      __typename    }    __typename  }}",
    }

    r = session.post(
        "https://www.redbox.com/gapi/ondemand/hcgraphql/",
        headers=headers,
        data=json.dumps(data),
    )
    js = r.json()["data"]["nearbyStores"]
    if not js:
        return []

    for j in js:
        j = j["store"]
        store_number = j.get("id") or "<MISSING>"
        j = j["profile"]

        a = j.get("location")
        street_address = a.get("address") or "<MISSING>"
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("zip") or "<MISSING>"
        country_code = "US"
        page_url = "<MISSING>"
        location_name = j.get("name") or j.get("vendor")
        phone = "<MISSING>"
        latitude = a.get("latitude") or "<MISSING>"
        longitude = a.get("longitude") or "<MISSING>"
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


def fetch_data():
    out = []
    s = set()
    coords = static_coordinate_list(radius=5, country_code=SearchableCountries.USA)

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, coord): coord for coord in coords}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                _id = row[8]
                if _id not in s:
                    s.add(_id)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
