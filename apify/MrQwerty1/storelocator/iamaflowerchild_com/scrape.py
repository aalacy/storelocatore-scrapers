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
    locator_domain = "https://www.iamaflowerchild.com/"
    api_url = "https://www.iamaflowerchild.com/api/?action=get-all-locations"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["data"]

    for j in js:
        page_url = j.get("permalink")
        j = j.get("location")

        street_address = j.get("address") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        location_name = j.get("displayName")
        phone = j.get("phone") or "<MISSING>"
        latitude, longitude = j.get("coordinates") or ["<MISSING>", "<MISSING>"]
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("hours", {})
        if hours:
            hours = hours.get(next(iter(hours)), {}) or {}

        for k, v in hours.items():
            if "Christmas" in k:
                continue
            _tmp.append(f"{k}: {v}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        status = j.get("customStatusMessage", "") or j.get(
            "statusIndicationMessageFriendly", ""
        )
        if "Temporarily" in status:
            hours_of_operation = "Temporarily Closed"
        if "Coming" in status:
            hours_of_operation = "Coming Soon"

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
