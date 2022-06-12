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

    locator_domain = "https://gogocurryamerica.com"
    api_url = "https://gogocurryamerica.com/wp-admin/admin-ajax.php?action=store_search&lat=40.75532&lng=-73.99329&max_results=50&search_radius=25&autoload=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = "https://gogocurryamerica.com/locations/"
        location_name = "".join(j.get("store")).replace("&#8217;", "`")
        location_type = "<MISSING>"
        street_address = f"{j.get('address')} {j.get('address2')}".replace(
            "None", ""
        ).strip()
        if location_name.find("Kitchen") != -1:
            street_address = street_address.split("!")[1].strip()
        if (
            street_address.find(
                "Our East 53rd location is still open for pickup & delivery!"
            )
            != -1
        ):
            street_address = "<MISSING>"
        phone = "".join(j.get("phone"))
        state = j.get("state")
        postal = "".join(j.get("zip"))
        if postal.find("-") != -1:
            postal = postal.split("-")[0].strip()
        country_code = j.get("country")
        city = j.get("city")
        store_number = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours = j.get("hours")
        try:
            hours = html.fromstring(hours)
            hours_of_operation = (
                " ".join(hours.xpath("//*/text()")).replace("\n", "").strip()
            )
        except TypeError:
            hours_of_operation = "<MISSING>"
        if location_name.find("*temporarily closed*") != -1:
            hours_of_operation = "temporarily closed"
            location_name = location_name.split("*")[0].strip()
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
