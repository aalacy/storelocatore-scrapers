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


def get_hours(_id):
    _tmp = []
    session = SgRequests()
    data = {"id": _id}
    r = session.post("https://www.konagrill.com/ajax/getlocationdetails", data=data)
    j = r.json()["data"]["dininghours"]
    hours = j.get("dining hours") or j.get("dining hours ") or []
    for h in hours:
        day = h.get("days")
        time = h.get("hours")
        if day.find("Brunch") != -1:
            continue
        _tmp.append(f"{day}: {time}")

    return ";".join(_tmp) or "<MISSING>"


def fetch_data():
    out = []
    locator_domain = "https://www.konagrill.com/"
    api_url = "https://www.konagrill.com/ajax/getalllocations"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["data"].values()

    for j in js:
        street_address = j.get("address") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("id")
        page_url = "https://www.konagrill.com/locations"
        location_name = j.get("title")
        phone = j.get("phone_number") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = get_hours(store_number)

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
