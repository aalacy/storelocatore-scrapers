import csv
import json

from datetime import datetime, timedelta
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


def override(js):
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    j = (
        json.loads(js.get("hours_sets:primary"))
        .get("children", {})
        .get("exception_hours")
        .get("overrides")
    )
    date_list = [
        (datetime.today() + timedelta(days=x)).date().strftime("%Y-%m-%d")
        for x in range(7)
    ]

    _tmp = []
    for date in date_list:
        day = days[datetime.strptime(date, "%Y-%m-%d").weekday()]
        if type(j.get(date)) == list:
            time = f"{j[date][0].get('open')} - {j[date][0].get('close')}"
            _tmp.append(f"{day}: {time}")
        else:
            _tmp.append(f"{day}: Closed")

    hoo = ";".join(_tmp)
    return hoo


def fetch_data():
    out = []
    url = "https://www.fleetpride.com/"
    api_url = "https://maps.branches.fleetpride.com/api/getAsyncLocations?template=search&level=search&search=75022&radius=10000&limit=5000"

    session = SgRequests()

    r = session.get(api_url)
    js_init = r.json()["maplist"]
    line = "[" + js_init.split('<div class="tlsmap_list">')[1].split(",</div>")[0] + "]"
    js = json.loads(line)

    s = set()
    for j in js:
        locator_domain = url
        page_url = j.get("url") or "<MISSING>"
        location_name = j.get("location_name") or "<MISSING>"
        street_address = (
            f"{j.get('address_1')} {j.get('address_2')}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("region") or "<MISSING>"
        postal = j.get("post_code") or "<MISSING>"
        country_code = "US"
        store_number = j.get("fid") or "<MISSING>"
        phone = j.get("local_phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = j.get("Store Type_CS") or "<MISSING>"
        if location_type == "Affiliates":
            continue

        _tmp = []
        tmp_js = json.loads(j.get("hours_sets:primary")).get("days", {})
        for day in tmp_js.keys():
            line = tmp_js[day]
            if len(line) == 1:
                start = line[0]["open"]
                close = line[0]["close"]
                _tmp.append(f"{day} {start} - {close}")
            else:
                _tmp.append(f"{day} Closed")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

        try:
            hours_of_operation = override(j)
        except:
            pass

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

        line = f"{location_name} {street_address} {city} {state} {postal}"
        if line not in s:
            s.add(line)
            out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
