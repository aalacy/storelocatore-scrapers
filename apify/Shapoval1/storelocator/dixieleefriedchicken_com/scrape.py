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
    locator_domain = "https://www.dixieleefriedchicken.com"
    api_url = "https://www.dixieleefriedchicken.com/wp-admin/admin-ajax.php?action=store_search&lat=45.049263&lng=-77.837555&max_results=25&search_radius=50&autoload=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": "https://www.dixieleefriedchicken.com/locations/",
        "TE": "Trailers",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        phone = j.get("phone") or "<MISSING>"
        street_address = f"{j.get('address')} {j.get('address2') or ''}".strip()
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        location_name = j.get("store") or "<MISSING>"
        country_code = j.get("country")
        store_number = j.get("id")
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = "<MISSING>"
        postal = j.get("zip")
        page_url = (
            f"https://www.dixieleefriedchicken.com/locations/#wpsl-id-{store_number}"
        )
        hours = j.get("hours") or "<MISSING>"
        if hours != "<MISSING>":
            hours = html.fromstring(hours)
            hours_of_operation = (
                " ".join(hours.xpath("//*//text()")).replace("\n", "").strip()
            )
        else:
            hours_of_operation = "<MISSING>"
        desc = "".join(j.get("description"))
        if "Temporarily Closed" in desc:
            hours_of_operation = "Temporarily Closed"

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
