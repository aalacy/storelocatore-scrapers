import csv
import json
import usaddress

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
    locator_domain = "https://insomniacookies.com/"

    tag = {
        "Recipient": "recipient",
        "AddressNumber": "address1",
        "AddressNumberPrefix": "address1",
        "AddressNumberSuffix": "address1",
        "StreetName": "address1",
        "StreetNamePreDirectional": "address1",
        "StreetNamePreModifier": "address1",
        "StreetNamePreType": "address1",
        "StreetNamePostDirectional": "address1",
        "StreetNamePostModifier": "address1",
        "StreetNamePostType": "address1",
        "CornerOf": "address1",
        "IntersectionSeparator": "address1",
        "LandmarkName": "address1",
        "USPSBoxGroupID": "address1",
        "USPSBoxGroupType": "address1",
        "USPSBoxID": "address1",
        "USPSBoxType": "address1",
        "BuildingName": "address2",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }
    headers = {"content-type": "application/json"}
    data = {
        "operationName": "stores",
        "variables": {"externalId": None, "customerId": None, "lat": lat, "lng": lng},
        "query": "query stores($lat: Float, $lng: Float, $externalId: String, $customerId: ID, $orderTypeId: ID) {  storeSearch(data: {lat: $lat, lng: $lng, externalId: $externalId, customerId: $customerId, orderTypeId: $orderTypeId}) {    lat    lng    address {      address1      city      state      postcode      lat      lng      __typename    }    stores {      id      name      address      distanceToStore      phone      storefrontImage      lat      lng      inDeliveryRange      boundary      status      note      storeType      isPickupOpen      isDeliveryOpen      hours {        type        days {          day          hour          __typename        }        __typename      }      __typename    }    __typename  }}",
    }

    r = session.post(
        "https://api.insomniacookies.com/graphql",
        headers=headers,
        data=json.dumps(data),
    )
    js = r.json()["data"]["storeSearch"]["stores"]
    for j in js:
        location_name = j.get("name")
        line = j.get("address")
        a = usaddress.tag(line, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
        if street_address == "None":
            street_address = "<MISSING>"
        city = a.get("city") or "<INACCESSIBLE>"
        state = a.get("state") or "<INACCESSIBLE>"
        postal = a.get("postal") or "<INACCESSIBLE>"
        country_code = "US"
        store_number = j.get("id")
        page_url = f"https://insomniacookies.com/locations/store/{store_number}"
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = "<MISSING>"

        _tmp = []
        days = []
        hours = j.get("hours")
        for h in hours:
            _type = h.get("type") or ""
            if "Retail" in _type:
                days = h.get("days")
                break

        for d in days:
            day = d.get("day")
            hour = d.get("hour")
            if hour.count("Closed") == 2:
                hour = "Closed"
            _tmp.append(f"{day}: {hour}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
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
    coords = static_coordinate_list(radius=20, country_code=SearchableCountries.USA)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
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
