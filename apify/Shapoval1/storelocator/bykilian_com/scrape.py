import csv
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

    locator_domain = "https://www.bykilian.com"
    api_url = (
        "https://www.bykilian.com/rpc/jsonrpc.tmpl?dbgmethod=locator.doorsandevents"
    )
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.bykilian.com/stores",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.bykilian.com",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers",
    }
    data = {
        "JSONRPC": '[{"method":"locator.doorsandevents","id":4,"params":[{"fields":"DOOR_ID, DOORNAME, EVENT_NAME, EVENT_START_DATE, EVENT_END_DATE, EVENT_IMAGE, EVENT_FEATURES, EVENT_TIMES, SERVICES, STORE_HOURS, ADDRESS, ADDRESS2, STATE_OR_PROVINCE, CITY, REGION, COUNTRY, ZIP_OR_POSTAL, PHONE1, STORE_TYPE, LONGITUDE, LATITUDE","radius":"100000","country":"USA","latitude":40.75368539999999,"longitude":-73.9991637}]}]'
    }
    r = session.post(api_url, headers=headers, data=data)
    js = r.json()
    s = set()
    for j in js[0]["result"]["value"]["results"].values():

        page_url = "https://www.bykilian.com/stores"
        location_name = j.get("DOORNAME") or "<MISSING>"
        location_type = j.get("STORE_TYPE") or "<MISSING>"
        if location_type == "FSS":
            location_type = "Boutique Kilian Store".capitalize()

        street_address = (
            f"{j.get('ADDRESS')} {j.get('ADDRESS2')}".strip() or "<MISSING>"
        )
        if "87-135 Brompton Rd" in street_address:
            location_type = "Boutique Kilian Store".capitalize()
        state = j.get("STATE_OR_PROVINCE") or "<MISSING>"
        postal = j.get("ZIP_OR_POSTAL") or "<MISSING>"
        country_code = j.get("COUNTRY") or "<MISSING>"
        city = j.get("CITY") or "<MISSING>"
        store_number = "<MISSING>"
        latitude = j.get("LATITUDE") or "<MISSING>"
        longitude = j.get("LONGITUDE") or "<MISSING>"
        phone = j.get("PHONE1") or "<MISSING>"
        hours_of_operation = j.get("STORE_HOURS") or "<MISSING>"

        line = street_address
        if line in s:
            continue
        s.add(line)

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
