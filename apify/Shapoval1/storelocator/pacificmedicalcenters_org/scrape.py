import csv
import re
from bs4 import BeautifulSoup
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

    locator_domain = "https://www.pacificmedicalcenters.org"
    api_url = "https://www.pacificmedicalcenters.org/wp-admin/admin-ajax.php?action=store_search&lat=47.55259&lng=-122.30094&max_results=25&search_radius=50&autoload=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = j.get("permalink")
        location_name = "".join(j.get("store")).replace("&#038;", "&")
        location_type = "Pacific Medical Center"
        street_address = f"{j.get('address')} {j.get('address2')}".strip()
        state = j.get("state")
        postal = j.get("zip")
        country_code = j.get("country")
        city = j.get("city")
        store_number = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")

        hours_of_operation = "".join(j.get("hours"))
        h = html.fromstring(hours_of_operation)
        hours_of_operation = " ".join(h.xpath("//*//text()")).replace("\n", "").strip()

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")
        try:
            phone = re.findall(
                r"[(\d)]{5} [\d]{3}-[\d]{4}", str(soup.find(class_="page-content"))
            )[0]
        except:
            phone = "<MISSING>"

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
