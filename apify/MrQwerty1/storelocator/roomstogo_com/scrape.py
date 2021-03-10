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
    locator_domain = "https://www.roomstogo.com/"
    api_url = "https://www.roomstogo.com/page-data/stores/page-data.json"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["result"]["pageContext"]["stores"]
    abbr = js["abbrevStates"]
    sts = js["states"]
    states = {k: v.lower().replace(" ", "-") for k, v in zip(abbr, sts)}
    js = js["stores"]

    for j in js:
        street_address = (
            f"{j.get('address1')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("storeNumber") or "<MISSING>"
        location_type = j.get("storeType") or "<MISSING>"
        city_url = city.lower().replace(" ", "-", 1)
        state_url = states.get(state)
        name = j.get("storeName") or ""
        if name:
            location_name = f"{city} - {name} {location_type}"
            name = name.lower().replace(" ", "-")
            page_url = f"https://www.roomstogo.com/stores/{state_url}/{city_url}-{name}-{location_type.lower()}-{store_number}"
        else:
            location_name = f"{city} {location_type}"
            page_url = f"https://www.roomstogo.com/stores/{state_url}/{city_url}-{location_type.lower()}-{store_number}"
        phone = j.get("phoneNumber") or "<MISSING>"
        loc = j.get("location")
        latitude = loc.get("lat") or "<MISSING>"
        longitude = loc.get("lon") or "<MISSING>"

        _tmp = []
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        h = j.get("storeHours", {}) or {}

        for d in days:
            start = h.get(f"{d}Open")
            close = h.get(f"{d}Closed")
            if start:
                _tmp.append(f"{d.capitalize()}: {start}-{close}")
            else:
                _tmp.append(f"{d.capitalize()}: Closed")

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
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
