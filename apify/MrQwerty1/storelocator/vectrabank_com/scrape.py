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
    locator_domain = "https://www.vectrabank.com/"
    page_url = "https://www.vectrabank.com/branch-locator/"
    api_url = "https://www.vectrabank.com/locationservices/searchwithfilter"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept": "*/*",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.vectrabank.com/branch-locator/",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.vectrabank.com",
        "Connection": "keep-alive",
        "TE": "Trailers",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    data = {
        "channel": "Online",
        "schemaVersion": "1.0",
        "clientUserId": "ZIONPUBLICSITE",
        "clientApplication": "ZIONPUBLICSITE",
        "transactionId": "txId",
        "affiliate": "0013",
        "searchResults": "2000",
        "username": "ZIONPUBLICSITE",
        "searchAddress": {
            "address": "75022",
            "city": None,
            "stateProvince": None,
            "postalCode": None,
            "country": None,
        },
        "distance": "5000",
        "searchFilters": [
            {"fieldId": "1", "domainId": "113", "displayOrder": 1, "groupNumber": 1}
        ],
    }

    session = SgRequests()
    r = session.post(api_url, headers=headers, data=json.dumps(data))
    js = r.json()["location"]

    for j in js:
        street_address = j.get("address") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("stateProvince") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        store_number = j.get("locationId") or "<MISSING>"
        location_name = j.get("locationName")
        if "ATM" in location_name:
            continue

        phone = j.get("phoneNumber") or "<MISSING>"
        if ":" in phone:
            phone = phone.split(":")[-1].strip()
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("long") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        text = j.get("locationAttributes") or []
        for t in text:
            n = t.get("name") or ""
            if n == "Lobby Hours":
                hours_of_operation = t.get("value")
                break

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
