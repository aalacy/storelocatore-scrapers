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
    locator_domain = "https://www.groupeproxim.ca"
    cookies = {"website#lang": "en"}
    api_url = "https://www.groupeproxim.ca/api/sitecore/Pharmacy/Pharmacies?id=%7B1F6A5AA6-C61C-4E22-8A30-C8C17CD9BCD9%7D"

    session = SgRequests()
    r = session.get(api_url, cookies=cookies)
    js = r.json()["pharmacies"]

    for j in js:
        location_name = j.get("title")
        a = j.get("address").split(",")
        postal = a.pop().strip()
        state = a.pop().replace("(", "").replace(")", "").strip()
        city = a.pop().strip()
        street_address = ", ".join(a).strip()
        country_code = "CA"
        store_number = j.get("storeCode") or "<MISSING>"
        slug = j.get("detailUrl") or ""
        page_url = f"{locator_domain}{slug}"
        phone = j.get("phone") or "<MISSING>"
        loc = j.get("location")
        latitude = loc.get("lat") or "<MISSING>"
        longitude = loc.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("storeOpeningHours") or []
        for h in hours:
            day = h.get("day")
            time = h.get("openDuration")
            if time == "Not available":
                continue
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
