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
    url = "https://christushealth.org/"
    api_url = "https://christushealth.org/~/locations/%7BFA392008-735A-4839-B72D-2E06304BCB4C%7D.ashx"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["points"]

    for j in js:
        loc = j.get("locations")
        for l in loc:
            locator_domain = url
            street_address = (
                f"{l.get('street')} {l.get('street2') or ''}".strip() or "<MISSING>"
            )
            line = j.get("cityState") or "<MISSING>,<MISSING>"
            city = line.split(",")[0].strip() or "<MISSING>"
            state = line.split(",")[1].strip() or "<MISSING>"
            postal = j.get("zip") or "<MISSING>"
            if len(postal) > 5:
                postal = postal[:5]
            country_code = "US"
            store_number = "<MISSING>"
            page_url = f'https://christushealth.org{l.get("detailLink")}'
            location_name = l.get("name") or "<MISSING>"
            phone = l.get("phone") or "<MISSING>"
            latitude = j.get("lat") or "<MISSING>"
            longitude = j.get("lng") or "<MISSING>"
            location_type = j.get("locationType") or "<MISSING>"
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
