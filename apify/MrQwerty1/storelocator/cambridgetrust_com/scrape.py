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
    locator_domain = "https://www.cambridgetrust.com/"
    api_url = "https://www.cambridgetrust.com/siteAPI/Branch/Branches"
    data = {"Location": "02139"}

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json;charset=utf-8",
        "Origin": "https://www.cambridgetrust.com",
        "Connection": "keep-alive",
        "Referer": "https://www.cambridgetrust.com/findlocation",
        "TE": "Trailers",
    }
    session = SgRequests()
    r = session.post(api_url, headers=headers, data=json.dumps(data))
    js = json.loads(r.text)
    js = json.loads(js)["Branches"]

    for j in js:
        street_address = j.get("StreetAddress") or "<MISSING>"
        city = j.get("City") or "<MISSING>"
        state = j.get("State") or "<MISSING>"
        postal = j.get("Zipcode") or "<MISSING>"
        country_code = "US"
        slug = j.get("Path") or ""
        page_url = f"https://www.cambridgetrust.com{slug}"
        store_number = "<MISSING>"
        location_name = j.get("Name")
        phone = j.get("PhoneFormatted") or "<MISSING>"
        latitude = j.get("Lat") or "<MISSING>"
        longitude = j.get("Lng") or "<MISSING>"
        location_type = j.get("Type") or "<MISSING>"
        if location_type == "ATM":
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
        for d in days:
            time = j.get(f"Hours{d}")
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
