import csv
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


def get_address(line):
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

    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
    if street_address == "None":
        street_address = "<MISSING>"
    city = a.get("city") or "<MISSING>"
    state = a.get("state") or "<MISSING>"
    postal = a.get("postal") or "<MISSING>"

    return street_address, city, state, postal


def get_hours(_id):
    _tmp = []
    session = SgRequests()
    data = {"id": _id}
    days = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]

    r = session.post("https://suzukicycles.com/api/dealer/GetLocationInfo", data=data)
    js = r.json()["LocationHours"]
    for j in js:
        index = j.get("DayOfWeek")
        if j.get("Closed"):
            _tmp.append(f"{days[index]}: Closed")
        else:
            start = j.get("OpenTime")
            end = j.get("CloseTime")
            _tmp.append(f"{days[index]}: {start} - {end}")

    return ";".join(_tmp) or "<MISSING>"


def get_data(coord):
    rows = []
    locator_domain = "https://suzukicycles.com/"
    page_url = "<MISSING>"
    lat, lng = coord

    data = {
        "itemId": "{C33D4122-B62A-48CE-9402-B3A137850A49}",
        "center": f"{lat},{lng}",
        "radius": "200",
        "parameters": '{"DealerTypes":"{DA1B1E9A-5E57-4B56-8D21-5CF7B214C028}|{47B7EC43-381A-4F4D-AE13-8CDB71515CB4}|{68BB96CA-C67C-4CE5-833C-223AAF66EA32}|{EBE0DAF5-225D-4A03-B075-52DFF1F8E0F5}","MapType":"roadmap","CenterLocation":'
        + f'"{lat}, {lng}"'
        + ',"ZoomLevel":"12","SearchRadius":"200","EnableCenterMapControl":"1","EnableZoomControl":"1","EnableMapTypeControl":"1","EnableScaleControl":"1","EnableStreetViewControl":"1","Dealer_Types":"{DA1B1E9A-5E57-4B56-8D21-5CF7B214C028}|{47B7EC43-381A-4F4D-AE13-8CDB71515CB4}|{68BB96CA-C67C-4CE5-833C-223AAF66EA32}|{EBE0DAF5-225D-4A03-B075-52DFF1F8E0F5}","EnableRotateControl":"0"}',
    }

    session = SgRequests()
    r = session.post("https://suzukicycles.com/api/dealer/DealerLookup", data=data)
    js = r.json()

    for j in js:
        location_name = j.get("Name")
        line = j.get("Address")
        street_address, city, state, postal = get_address(line.replace("\n", " "))
        country_code = "US"
        store_number = j.get("LocationID") or "<MISSING>"
        phone = j.get("PhoneFormatted") or "<MISSING>"
        try:
            latitude, longitude = j.get("Location").split(",")
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
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
    _tmp = []
    out = []
    hours = dict()
    s = set()
    coords = static_coordinate_list(radius=50, country_code=SearchableCountries.USA)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, coord): coord for coord in coords}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                _id = row[8]
                if _id not in s:
                    s.add(_id)
                    _tmp.append(row)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_hours, _id): _id for _id in s}
        for future in futures.as_completed(future_to_url):
            _id = future_to_url[future]
            try:
                val = future.result()
            except:
                val = "<MISSING>"
            hours[_id] = val

    for t in _tmp:
        _id = t[8]
        if _id != "<MISSING>":
            t[-1] = hours.get(_id) or "<MISSING>"
        out.append(t)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
