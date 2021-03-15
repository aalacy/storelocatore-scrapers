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
    locator_domain = "https://www.fullers.co.uk/"
    page_url = "https://www.fullers.co.uk/pubs/old-pub-finder"
    api_url = "https://www.fullers.co.uk/api/sitecore/findpubs?id=%7B07DC99EB-8AA2-42F4-B9A6-9D3648ABD465%7D&mode=LocationPub&filters=-1%2CStanding%2C&myPosition=(51.507351%2C+-0.127758)&position=(51.507351%2C+-0.127758)&nePosition=(52.68834732924637%2C+3.56090166796875)&swPosition=(50.29492984990391%2C+-3.81641766796875)&defaultRadius=&zoomLevel=8&findNearMe=false&pageHeading="

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["pubs"]

    for j in js:
        street_address = (
            f"{j.get('PubAddressLine1')} {j.get('PubAddressLine2') or ''}".strip()
            or "<MISSING>"
        )
        city = j.get("PubAddressCity") or "<MISSING>"
        state = j.get("PubAddressCounty") or "<MISSING>"
        postal = j.get("PubAddressPostcode") or "<MISSING>"
        country_code = "GB"
        store_number = j.get("PubId") or "<MISSING>"
        location_name = j.get("PubSignageName")
        if not location_name:
            continue
        phone = j.get("PubContactTelephone") or "<MISSING>"
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

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
