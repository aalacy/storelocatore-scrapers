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

    locator_domain = "https://www.medicalpharmacies.com/"
    api_url = "https://www.medicalpharmacies.com/wp-admin/admin-ajax.php?action=store_search&lat=48.40794&lng=-89.252564&max_results=500&search_radius=50000&autoload=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:

        page_url = "https://www.medicalpharmacies.com/about/locations/"
        location_name = j.get("store")
        street_address = j.get("address")
        phone = "".join(j.get("phone")) or "<MISSING>"
        if phone.find("/") != -1:
            phone = phone.split("/")[0].strip()
        state = j.get("state")
        postal = j.get("zip")
        country_code = "CA"
        city = "".join(j.get("city")).replace(",", "").strip()
        id = j.get("id")
        store_number = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = j.get("hours") or "<MISSING>"
        if hours_of_operation != "<MISSING>":
            a = html.fromstring(hours_of_operation)
            hours_of_operation = (
                " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
            )

        session = SgRequests()
        r = session.get(
            "https://www.medicalpharmacies.com/about/locations/", headers=headers
        )
        tree = html.fromstring(r.text)

        location_type = (
            "".join(
                tree.xpath(
                    f'//div[@class="loc-grid data-store-id-{id}"]//span[@class="location-type"]/text()'
                )
            )
            .replace("\n", "")
            .strip()
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
