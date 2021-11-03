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

    locator_domain = "https://www.buckortwo.com/"
    api_url = "https://www.buckortwo.com/wp-admin/admin-ajax.php?lang=en&action=store_search&lat=43.65323&lng=-79.38318&max_results=500&search_radius=5000&autoload=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:

        page_url = "https://www.buckortwo.com/store-locator/"
        location_name = (
            "".join(j.get("store")).replace("&#038;", "&").replace("&#8211;", "–")
        )
        street_address = f"{j.get('address')} {j.get('address2')}".strip()
        phone = "".join(j.get("phone")) or "<MISSING>"
        if phone.find("/") != -1:
            phone = phone.split("/")[0].strip()
        state = j.get("state")
        postal = j.get("zip")
        country_code = "CA"
        city = "".join(j.get("city")).replace(",", "").strip()
        store_number = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = j.get("hours") or "<MISSING>"
        if hours_of_operation != "<MISSING>":
            a = html.fromstring(hours_of_operation)
            hours_of_operation = (
                " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
            )

        location_type = "<MISSING>"

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
