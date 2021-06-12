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
    locator_domain = "https://www.miracle-ear.com/"
    api_url = "https://www.miracle-ear.com/stores-near-me/results.getStores.json"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.miracle-ear.com/stores-near-me/results?addr=75022&lat=33.0218117&long=-97.12516989999999",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.miracle-ear.com",
        "Connection": "keep-alive",
        "TE": "Trailers",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    params = (
        ("addr", "75022"),
        ("lat", "33.0218117"),
        ("long", "-97.12516989999999"),
    )

    data = {
        "countryCode": "US",
        "latitude": "33.0218117",
        "longitude": "-97.12516989999999",
        "locale": "en_US",
        "limit": "2000",
        "radius": "8000000",
        "type": "",
    }

    session = SgRequests()
    r = session.post(api_url, headers=headers, data=data, params=params)
    js = r.json()

    for j in js:
        if not j.get("visible"):
            continue

        street_address = j.get("address") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("cap") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        store_number = j.get("shopNumber") or "<MISSING>"
        slug = j.get("shortName") or ""
        ain = j.get("AIN") or ""
        page_url = f"https://www.miracle-ear.com/stores-near-me/-/{slug}-s{ain}"
        location_name = j.get("shopName")
        phone = "<MISSING>"
        phones = j.get("phones") or []
        for p in phones:
            if p.get("primaryphone"):
                phone = p.get("phonenumber")
                break
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<INACCESSIBLE>"

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
