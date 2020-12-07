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
    url = "https://soma.com/"

    session = SgRequests()

    for i in range(0, 5000):
        api_url = f"https://soma.brickworksoftware.com/locations_search?esSearch="
        params = {
            "page": i,
            "storesPerPage": 50,
            "domain": "soma.brickworksoftware.com",
            "must": [
                {
                    "type": "range",
                    "field": "published_at",
                    "value": {"lte": 1607376261444},
                }
            ],
        }

        params = json.dumps(params)
        r = session.get(f"{api_url}{params}")
        js = r.json()["hits"]

        for j in js:
            locator_domain = url
            a = j.get("attributes")
            location_name = a.get("name") or "<MISSING>"
            slug = a.get("slug")
            page_url = f"https://stores.soma.com/boutique/{slug}"
            adr1, adr2 = a.get("address1") or "", a.get("address2") or ""
            street_address = f"{adr1} {adr2}".strip() or "<MISSING>"
            city = a.get("city") or "<MISSING>"
            state = a.get("state") or "<MISSING>"
            postal = a.get("postalCode") or "<MISSING>"
            country_code = a.get("countryCode") or "<MISSING>"
            store_number = j.get("id") or "<MISSING>"
            phone = a.get("phoneNumber") or "<MISSING>"
            loc = j.get("_geoloc")
            latitude = loc.get("lat") or "<MISSING>"
            longitude = loc.get("lng") or "<MISSING>"
            location_type = "<MISSING>"

            _tmp = []
            hours = j.get("relationships", {}).get("hours", []) or []
            for h in hours:
                day = h.get("displayDay")
                start = h.get("displayStartTime")
                end = h.get("displayEndTime")
                _tmp.append(f"{day}: {start} -{end}")

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

        if len(js) < 50:
            break

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
