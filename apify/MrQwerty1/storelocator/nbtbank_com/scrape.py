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
    url = "https://www.nbtbank.com/"
    api_url = "https://www.nbtbank.com/content/branchResults.cshtml"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["features"]

    for j in js:
        geo = j.get("geometry", {}).get("coordinates") or ["<MISSING>", "<MISSING>"]
        j = j.get("properties")
        locator_domain = url
        location_name = j.get("name") or "<MISSING>"
        if location_name.find("ATM") != -1:
            continue
        street_address = (
            f"{j.get('address1')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        page_url = "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        latitude = geo[1]
        longitude = geo[0]
        location_type = "<MISSING>"

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
        for d in days:
            if d == "Tuesday":
                part = "Tues"
            elif d == "Thursday":
                part = "Thurs"
            else:
                part = d[:3]

            time = j.get(f"Lobby_{part}") or "Closed"
            _tmp.append(f"{d}: {time}")

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
