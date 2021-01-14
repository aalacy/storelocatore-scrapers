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
    locator_domain = "https://www.currys.co.uk"
    api_url = "https://api.currys.co.uk/store/api/stores?maxCount=5000&types=2in1-HS%2C2in1-MS%2C2in1-SS%2C3in1-HS%2C3in1-MS%2C3in1-SS%2CBLACK%2CCDG-HS%2CCUR-MS%2CCUR-SS%2CPCW-HS%2CPCW-SS"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["payload"]["stores"]

    for j in js:
        street_address = j.get("address") or "<MISSING>"
        city = j.get("town") or "<MISSING>"
        state = "<MISSING>"
        postal = j.get("postcode") or "<MISSING>"
        country_code = "GB"
        store_number = j.get("id") or "<MISSING>"
        page_url = (
            f"https://www.currys.co.uk/gbuk/store-finder/london/store-{store_number}"
        )
        location_name = f"Currys PC World, {city}"
        phone = "<MISSING>"
        loc = j.get("location")
        latitude = loc.get("latitude") or "<MISSING>"
        longitude = loc.get("longitude") or "<MISSING>"
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
        hours = j.get("standardOpeningHours") or []
        for h in hours:
            index = h.get("day") - 1
            day = days[index]
            start = h.get("from")
            close = h.get("to")
            _tmp.append(f"{day}: {start} - {close}")

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
