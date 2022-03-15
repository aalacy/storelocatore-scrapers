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
    s = set()
    url = "https://republicservices.com/"
    api_url = "https://www.republicservices.com/api/v1/localContent/facilities?latitude=40.9614&longitude=-93.1817&limit=5000"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["data"]

    for j in js:
        locator_domain = url
        page_url = "<MISSING>"
        location_name = j.get("facilityName") or "<MISSING>"
        if location_name.find(">") != -1 and location_name != "<MISSING>":
            location_name = location_name.split(">")[-2].split("<")[0]
        a = j.get("facilityAddress", {})
        street_address = a.get("addressLine", "<MISSING>").strip() or "<MISSING>"
        city = a.get("placeName") or "<MISSING>"
        state = a.get("stateCode") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        if len(postal) == 4:
            postal = f"0{postal}"
        country_code = a.get("countryName") or "<MISSING>"
        store_number = j.get("lawsonId")
        if not store_number or street_address == "<MISSING>":
            continue
        store_number = store_number.replace(" ", "")
        ph = j.get("phoneNumbers")
        if ph:
            phone = ph[0].get("phoneNumber")
            if len(phone) < 10:
                phone = "<MISSING>"
            elif phone == "0" * 10:
                phone = "<MISSING>"
        else:
            phone = "<MISSING>"
        g = j.get("geoLocation", {}) or {}
        latitude = g.get("latitude") or "<MISSING>"
        longitude = g.get("longitude") or "<MISSING>"
        operation = j.get("schedule", {}).get("operating")
        if operation:
            _tmp = []
            t = operation[0]["season"]
            start = t.get("timeBegin")
            end = t.get("timeEnd")
            days = t.get("daysOfWeek")
            for d in days:
                _tmp.append(f"{d}: {start} - {end}")

            hours_of_operation = ";".join(_tmp)
        else:
            hours_of_operation = "<MISSING>"

        types = j.get("facilityTypes", ["<MISSING>"]) or ["<MISSING>"]
        location_type = " | ".join(types)

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

        if store_number not in s:
            out.append(row)
            s.add(store_number)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
