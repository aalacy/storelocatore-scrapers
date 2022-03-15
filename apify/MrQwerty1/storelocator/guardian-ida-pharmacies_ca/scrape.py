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
    locator_domain = "https://www.guardian-ida-pharmacies.ca/"
    api_url = "https://www.guardian-ida-pharmacies.ca/api/sitecore/Pharmacy/Pharmacies?id=%7B17FEB0C2-8DF6-40C5-A641-3F78ED5699DA%7D"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["pharmacies"]

    for j in js:
        a = j.get("address").split(",")
        if len(a) < 4:
            continue

        postal = a.pop().strip()
        state = a.pop().replace("(", "").replace(")", "").strip()
        city = a.pop().strip()
        street_address = ",".join(a)
        country_code = "CA"

        store_number = j.get("storeCode") or "<MISSING>"
        page_url = f'https://www.guardian-ida-pharmacies.ca{j.get("detailUrl")}'
        location_name = j.get("titleEscaped")
        phone = j.get("phone") or "<MISSING>"
        loc = j.get("location") or {}
        latitude = loc.get("lat") or "<MISSING>"
        longitude = loc.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("storeOpeningHours") or []
        for h in hours:
            day = h.get("day")
            time = h.get("openDuration")
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

        check = tuple(row[2:6])
        if check not in s:
            out.append(row)
            s.add(check)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
