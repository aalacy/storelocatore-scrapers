import csv
import json

from concurrent import futures
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


def get_zones():
    zones = []
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Content-Type": "application/json",
        "Origin": "https://www.hilton.com",
    }

    data = '{"operationName":"hotelMapZones","variables":{"brandCode":"UP"},"query":"query hotelMapZones($brandCode: String) {\\n hotelMapZones(brandCode: $brandCode) {\\n id {\\n x\\n y\\n __typename\\n }\\n bounds {\\n southwest {\\n latitude\\n longitude\\n __typename\\n }\\n northeast {\\n latitude\\n longitude\\n __typename\\n }\\n __typename\\n }\\n countries {\\n countryCode\\n stateCodes\\n __typename\\n }\\n brandCodes\\n __typename\\n }\\n}\\n"}'

    r = session.post(
        "https://www.hilton.com/graphql/customer?appName=dx-shop-dream-ui&operationName=hotelMapZones",
        headers=headers,
        data=data,
    )

    js = r.json()["data"]["hotelMapZones"]
    for j in js:
        zones.append(j["id"])

    return zones


def get_data(zone):
    rows = []
    session = SgRequests()
    del zone["__typename"]
    locator_domain = "https://hilton.com/en/tapestry"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Content-Type": "application/json",
        "Origin": "https://www.hilton.com",
    }

    data = {
        "operationName": "hotelSummaryOptions",
        "variables": {
            "brandCodes": ["UP"],
            "currencyCode": "usd",
            "language": "en",
            "queryLimit": 0,
            "zone": zone,
        },
        "query": "query hotelSummaryOptions($brandCodes: [String!]!, $currencyCode: String!, $language: String!, $zone: HotelZoneInput) {  hotelSummaryOptions(brandCodes: $brandCodes, language: $language, input: {zone: $zone}) {    hotels {      _id: ctyhocn      amenityIds      brandCode      ctyhocn      currencyCode      distance      distanceFmt      homeUrl      name      phoneNumber      open      address {        addressFmt        addressLine1        addressLine2        city        country        countryName        postalCode        state        stateName        __typename      }      coordinate {        latitude        longitude        __typename      }      thumbnail: masterImage(variant: searchPropertyImageThumbnail) {        altText        variants {          size          url          __typename        }        __typename      }      leadRate {        lowest {          rateAmount(currencyCode: $currencyCode, decimal: 0, strategy: trunc)          rateAmountFmt(decimal: 0, strategy: trunc)          __typename        }        __typename      }      __typename    }    __typename  }}",
    }

    r = session.post(
        "https://www.hilton.com/graphql/customer?appName=dx-shop-dream-ui&operationName=hotelSummaryOptions&queryType=zone",
        headers=headers,
        data=json.dumps(data),
    )
    js = r.json()["data"]["hotelSummaryOptions"]["hotels"]

    for j in js:
        page_url = j.get("homeUrl")
        location_name = j.get("name")
        a = j.get("address") or {}
        street_address = (
            f'{a.get("addressLine1")} {a.get("addressLine2") or ""}'.strip()
            or "<MISSING>"
        )
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = a.get("country") or "<MISSING>"
        if not (country_code == "US" or country_code == "CA"):
            continue
        store_number = j.get("_id") or "<MISSING>"
        phone = j.get("phoneNumber") or "<MISSING>"
        geo = j.get("coordinate") or {}
        latitude = geo.get("latitude") or "<MISSING>"
        longitude = geo.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

        isopen = j.get("open")
        if not isopen:
            continue

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
    zones = get_zones()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, zone): zone for zone in zones}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
