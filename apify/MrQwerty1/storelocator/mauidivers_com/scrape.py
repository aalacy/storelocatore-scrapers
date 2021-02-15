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
    locator_domain = "https://www.mauidivers.com/"
    api_url = "https://stores.boldapps.net/front-end/get_surrounding_stores.php?shop=maui-divers-jewelry.myshopify.com&latitude=33.0218117&longitude=-97.12516989999999&limit=50"
    page_url = "https://www.mauidivers.com/apps/store-locator"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["stores"]

    for j in js:
        street_address = (
            f"{j.get('address')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("prov_state") or "<MISSING>"
        postal = j.get("postal_zip") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        location_name = j.get("name")
        if location_name.lower().find("closed") != -1:
            continue
        store_number = location_name.split("#")[-1].split()[0]
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("hours") or "\r\n"
        for h in hours.split("\r\n"):
            if h.find(":") == -1 and h.lower().find("daily") == -1:
                continue
            _tmp.append(" ".join(h.split()))
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
