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


def get_data():
    rows = []
    locator_domain = "https://freshslice.com/"
    api_url = "https://freshslice.com/wp-admin/admin-ajax.php?action=store_search&lat=49.26999&lng=-123.01829&max_results=25&search_radius=10&autoload=1"
    session = SgRequests()
    r = session.get(api_url)
    js = r.json()
    for j in js:
        street_address = f"{j.get('address')} {j.get('address2')}".replace(
            "None", ""
        ).strip()
        if street_address.find("110 – 435") != -1:
            street_address = street_address.split(",")[0].strip()

        city = "".join(j.get("city"))
        if city.find("Rocky") != -1:
            city = city.split()[0].strip()
        state = j.get("state")
        postal = j.get("zip")
        country_code = j.get("country")
        store_number = "<MISSING>"
        location_name = "".join(j.get("store")).replace("&#8211;", "-")
        phone = j.get("phone") or "<MISSING>"
        if phone.find("or") != -1:
            phone = phone.split("or")[0].strip()
        page_url = j.get("permalink")
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = "<MISSING>"
        hours = str(j.get("hours"))
        hours = html.fromstring(hours)
        hours_of_operation = " ".join(hours.xpath("//*//text()")).replace(
            "None", "<MISSING>"
        )
        if street_address.find("4140") != -1:
            hours_of_operation = "Coming Soon"

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

        rows.append(row)
    return rows


def scrape():
    data = get_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
