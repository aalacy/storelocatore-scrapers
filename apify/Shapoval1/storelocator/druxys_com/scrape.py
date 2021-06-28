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

    locator_domain = "https://druxys.com"
    api_url = "https://druxys.com/wp-admin/admin-ajax.php?action=store_search&lat=43.65323&lng=-79.38318&max_results=50&search_radius=100"
    page_url = "https://druxys.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:
        location_name = "".join(j.get("store")).replace("&#8211;", "–")
        location_type = "<MISSING>"
        street_address = f"{j.get('address')} {j.get('address2')}".strip()
        phone = "".join(j.get("phone"))
        if phone.find("ext") != -1:
            phone = phone.split("ext")[0].strip()
        state = j.get("state")
        postal = j.get("zip")
        country_code = j.get("country")
        city = j.get("city")
        store_number = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours = j.get("hours") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        hourses = ""
        if hourses != "<MISSING>":
            hourses = hours
        if hours != "<MISSING>":
            hourses = html.fromstring(hourses)
            hours_of_operation = (
                " ".join(hourses.xpath("//*/text()")).replace("\n", "").strip()
                or "<MISSING>"
            )
        if location_name.find("Temporarily Closed") != -1:
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
