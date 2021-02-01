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
    locator_domain = "https://myhoneyfarms.com/locations/"
    api_url = "https://myhoneyfarms.com/wp-admin/admin-ajax.php?action=store_search&lat=40.75369&lng=-73.99916&max_results=100&search_radius=1000"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        street_address = (
            f"{j.get('address')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        if country_code == "United States":
            country_code = "US"

        store_number = j.get("id")
        page_url = j.get("permalink")
        location_name = "".join(j.get("store")).replace("&#8211;", "-")
        phone = j.get("phone")

        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"
        tmp = []
        text = j.get("hours")
        tree = html.fromstring(text)
        divs = tree.xpath("//text()")
        for d in divs:
            tmp.append(d)
        hours_of_operation = " ".join(tmp) or "<MISSING>"

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
