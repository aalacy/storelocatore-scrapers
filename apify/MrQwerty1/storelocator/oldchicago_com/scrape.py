import csv
import json

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


def fetch_data():
    out = []
    session = SgRequests()
    locator_domain = "https://oldchicago.com"
    api_url = "https://oc-api-prod.azurewebsites.net/graphql"
    headers = {"Content-Type": "application/json"}

    data = {
        "query": 'query LocationList_ViewerRelayQL($id_0:ID!) {node(id:$id_0) {...F0}} fragment F0 on Viewer {_locations3pwhxm:locations(first:1500,geoString:"") {edges {node {id,slug,locationId,title,isOpen,latitude,longitude,simpleHours {days,hours,id},distance,distancefromSearch,searchLatitude,searchLongitude,phone,address {route,streetNumber,stateCode,stateName,city,postalCode,id},comingSoon},cursor},pageInfo {hasNextPage,hasPreviousPage}},id}',
        "variables": {"id_0": "Vmlld2VyOjA="},
    }

    r = session.post(api_url, headers=headers, data=json.dumps(data))

    js = r.json()["data"]["node"]["_locations3pwhxm"]["edges"]

    for j in js:
        j = j["node"]
        a = j.get("address")
        street_address = f"{a.get('streetNumber')} {a.get('route') or ''}".strip()
        city = a.get("city") or "<MISSING>"
        state = a.get("stateCode") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = "US"
        store_number = j.get("locationId") or "<MISSING>"
        page_url = f'https://oldchicago.com/locations/{j.get("slug")}'
        location_name = j.get("title")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("simpleHours", []) or []
        for h in hours:
            day = h.get("days")
            time = h.get("hours")
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
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
