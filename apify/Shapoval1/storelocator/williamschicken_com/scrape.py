import csv
from lxml import html
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

    locator_domain = "https://williamschicken.com"
    api_url = "https://williamschicken.com/wcnewwp/wp-admin/admin-ajax.php?action=store_search&lat=32.77666&lng=-96.79699&max_results=5&search_radius=50&autoload=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = j.get("permalink") or "https://williamschicken.com/locations/"
        location_name = j.get("store") or "<MISSING>"
        location_type = "<MISSING>"
        street_address = (
            f"{j.get('address')} {j.get('address2')}".strip() or "<MISSING>"
        )
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        city = j.get("city") or "<MISSING>"
        store_number = location_name.split("#")[1].strip()
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        hours_of_operation = j.get("hours") or "<MISSING>"
        if hours_of_operation != "<MISSING>":
            a = html.fromstring(hours_of_operation)
            hours_of_operation = (
                " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
            )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = j.get("store_custom_message") or "<MISSING>"
        if hours_of_operation == "Seasonal" or hours_of_operation == "Call for Hours":
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
