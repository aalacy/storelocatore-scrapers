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

    locator_domain = "https://tractorfoods.com"
    api_url = "https://order.tractorfoods.com/api/vendors/regions?excludeCities=true"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "application/json, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "__RequestVerificationToken": "",
        "X-Requested-With": "XMLHttpRequest",
        "X-Olo-Request": "1",
        "X-Olo-Viewport": "Desktop",
        "X-Olo-App-Platform": "web",
        "Connection": "keep-alive",
        "Referer": "https://order.tractorfoods.com/locations",
        "TE": "Trailers",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:
        state = j.get("code")

        session = SgRequests()
        r = session.get(
            f"https://order.tractorfoods.com/api/vendors/search/{state}",
            headers=headers,
        )
        js = r.json()["vendor-search-results"]
        for j in js:
            slug = j.get("slug")
            page_url = f"https://order.tractorfoods.com/menu/{slug}"
            location_name = j.get("name")
            location_type = "<MISSING>"
            street_address = j.get("streetAddress")
            phone = j.get("phoneNumber")
            postal = j.get("address").get("postalCode")
            country_code = j.get("address").get("country")
            city = j.get("city")
            store_number = "<MISSING>"
            latitude = j.get("latitude")
            longitude = j.get("longitude")
            hours = j.get("weeklySchedule").get("calendars")[0].get("schedule")
            tmp = []
            for h in hours:

                day = h.get("weekDay")
                times = h.get("description")
                line = f"{day} {times}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp) or "<MISSING>"
            if hours_of_operation.count("Closed") == 7:
                hours_of_operation = "Closed"
            if hours_of_operation == "Closed":
                continue

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
