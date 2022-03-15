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
    locator_domain = "https://toujoursmikes.ca/en/"
    api_url = "https://toujoursmikes.ca/service/search/branch?page=all&lang=en"
    location_type = "<MISSING>"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://toujoursmikes.ca/en/find-a-restaurant",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "TE": "Trailers",
    }

    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        ad = j.get("address")
        street_address = ad.get("address")
        phone = j.get("phone")
        city = ad.get("city")
        postal = ad.get("zip")
        slug = j.get("slug")
        state = ad.get("province")
        country_code = ad.get("country")
        store_number = "<MISSING>"
        page_url = f"{locator_domain}{slug}"
        location_name = j.get("title")
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours = j.get("schedule").get("week")
        tmp = []
        for h in hours:
            days = h
            try:
                opens = (
                    j.get("schedule")
                    .get("week")[h]
                    .get("dining")
                    .get("range")[0]
                    .get("from")
                )
                closes = (
                    j.get("schedule")
                    .get("week")[h]
                    .get("dining")
                    .get("range")[0]
                    .get("to")
                )
            except IndexError:
                opens = "Closed"
                closes = "Closed"
            line = f"{days} : {opens} - {closes}"
            if line.count("Closed") == 2:
                line = f"{days} - Closed"
            tmp.append(line)
        hours_of_operation = ";".join(tmp) or "<MISSING>"
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
