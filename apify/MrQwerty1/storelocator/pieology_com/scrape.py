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

    locator_domain = "https://pieology_com"
    api_url = "https://order.pieology.com/api/vendors/regions?excludeCities=true"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept": "application/json, */*",
        "__RequestVerificationToken": "",
        "X-Olo-Request": "1",
    }

    r = session.get(api_url, headers=headers)
    states = r.json()

    for state in states:
        state_code = state.get("code")
        session = SgRequests()
        r = session.get(
            f"https://order.pieology.com/api/vendors/search/{state_code}",
            headers=headers,
        )
        js = r.json()["vendor-search-results"]

        for j in js:
            a = j.get("address")
            page_url = f"https://order.pieology.com/locations/{state_code}"
            location_name = j.get("name") or "<MISSING>"
            location_type = "<MISSING>"
            street_address = (
                f"{a.get('streetAddress')} {a.get('streetAddress2') or ''}".strip()
            )
            phone = j.get("phoneNumber") or "<MISSING>"
            state = a.get("state") or "<MISSING>"
            postal = a.get("postalCode") or "<MISSING>"
            country_code = a.get("country") or "<MISSING>"
            city = a.get("city") or "<MISSING>"
            store_number = "<MISSING>"
            latitude = j.get("latitude") or "<MISSING>"
            longitude = j.get("longitude") or "<MISSING>"
            hours = j.get("weeklySchedule").get("calendars")[0].get("schedule")
            tmp = []
            for h in hours:
                day = h.get("weekDay")
                time = h.get("description")
                line = f"{day}: {time}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp) or "<MISSING>"

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
