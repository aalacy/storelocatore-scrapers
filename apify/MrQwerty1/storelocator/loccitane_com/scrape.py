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
    locator_domain = "https://www.loccitane.com/"
    api_url = "https://www.loccitane.com/on/demandware.store/Sites-OCC_US-Site/en_US/Stores-GetStores?countryCode=US"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
    }

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    js = r.json()["stores"]

    for j in js:
        location_name = j.get("name")
        street_address = (
            f"{j.get('address1')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("stateCode") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        if len(postal) == 4:
            postal = f"0{postal}"
        country_code = "US"
        store_number = j.get("ID") or "<MISSING>"
        page_url = f"https://www.loccitane.com/on/demandware.store/Sites-OCC_US-Site/en_US/Stores-ShowStore?id={store_number}"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"

        c = j.get("custom") or {}
        location_type = c.get("OCC_category") or "<MISSING>"
        if location_type not in {"Boutique", "Outlet"}:
            continue

        _tmp = []
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        text = c.get("OCC_openingHours") or '{"Standard":{}}'

        try:
            _js = json.loads(text)["Standard"]
            for k, v in _js.items():
                index = int(k) - 1
                day = days[index]
                time = v.get("am")
                if time:
                    _tmp.append(f"{day}: {time}")
                else:
                    _tmp.append(f"{day}: Closed")
        except KeyError:
            _tmp.append("Closed")

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
