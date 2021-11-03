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


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def fetch_data():
    out = []
    locator_domain = "https://allianceurgentcare.com/"
    api_url = "https://allianceurgentcare.com/assets/data/facilitiesData.json"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["Facilities"]

    for j in js:
        location_name = j.get("FacilityName")
        if "Locations" in location_name:
            continue

        street_address = (
            f"{j.get('FacilityAddress')} {j.get('FacilitySuite') or ''}".strip()
            or "<MISSING>"
        )
        city = j.get("FacilityCity") or "<MISSING>"
        state = j.get("FacilityState") or "<MISSING>"
        postal = j.get("FacilityZip") or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        page_url = f'https://allianceurgentcare.com{j.get("FacilityWebPage")}'
        phone = j.get("FacilityPhone") or "<MISSING>"
        text = j.get("FacilityEmbedMapUrl") or ""
        latitude, longitude = get_coords_from_embed(text)
        location_type = "<MISSING>"
        hours_of_operation = (
            f'{j.get("FacilityWeekDayHours") or ""};{j.get("FacilityWeekEndHours") or ""}'.strip()
            or "<MISSING>"
        )

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
