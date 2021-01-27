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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/json",
    }

    data = '{"Parameters":[{"DealerId":"","Distance":"5000","Keyword":"","Latitude":33.0218117,"Longitude":-97.12516989999999,"ServiceGroupName":"","ServiceType":"","Category":"Bank","AdditionalCategory":"","SortBy":"StoreDistance","SortOrder":"asc","StoreId":"","DistanceCalType":"airdistance"},{"DealerId":"","Keyword_Lookup":"StoreName","Keyword_Oprator":"or","Distance":"5000","Keyword":"Commerce Bank","Latitude":33.0218117,"Longitude":-97.12516989999999,"ServiceGroupName":"","ServiceType":"","Category":"Bank","AdditionalCategory":"","SortBy":"StoreDistance","SortOrder":"asc","StoreId":"","DistanceCalType":"airdistance"}]}'

    locator_domain = "https://www.ibc.com"
    api_url = "https://www.ibc.com/Api/LocationApi/GetLocation"

    session = SgRequests()
    r = session.post(api_url, headers=headers, data=data)
    js = r.json()["Locations"]

    for j in js:
        street_address = j.get("Address") or "<MISSING>"
        city = j.get("City") or "<MISSING>"
        state = j.get("StateCode") or "<MISSING>"
        postal = j.get("ZipCode") or "<MISSING>"
        country_code = j.get("Country") or "<MISSING>"
        if country_code == "United States":
            country_code = "US"

        store_number = j.get("StoreId") or "<MISSING>"
        page_url = f"https://www.ibc.com/atm-branch-detail?locationid={store_number}"
        location_name = j.get("StoreName") or "<MISSING>"
        phone = j.get("ContactNo") or "<MISSING>"
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        location_type = j.get("StoreCategory") or "<MISSING>"

        _tmp = []
        hours = j.get("BusinessHoursList", []) or []
        for h in hours:
            day = h.get("WeekDayName")
            start = h.get("Opens")
            end = h.get("closes")
            _tmp.append(f"{day}: {start} - {end}")

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
