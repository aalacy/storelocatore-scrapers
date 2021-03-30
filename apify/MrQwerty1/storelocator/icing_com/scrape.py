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
    url = "https://stores.icing.com/us/"
    api_url = "https://maps.stores.claires.com/api/getAsyncLocations?template=searchicing&level=search&limit=*&radius=*"

    session = SgRequests()

    r = session.get(api_url)
    js_init = r.json()["maplist"]
    js = json.loads("[" + js_init.split(">")[1].split("<")[0][:-1] + "]")

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
        country_code = j.get("country") or "<MISSING>"
        store_number = j.get("fid").replace("na", "")
        phone = j.get("local_phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        tmp_js = json.loads(j.get("hours_sets:primary")).get("days") or {}
        for day in tmp_js.keys():
            line = tmp_js[day]
            if len(line) == 1:
                start = line[0]["open"]
                close = line[0]["close"]
                _tmp.append(f"{day} {start} - {close}")
            else:
                _tmp.append(f"{day} Closed")

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
