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

    locator_domain = "https://www.avitapharmacy.com"
    api_url = "https://www.avitapharmacy.com/wp-admin/admin-ajax.php?action=store_search&lat=37.09024&lng=-95.71289&max_results=25&search_radius=50&autoload=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = "https://www.avitapharmacy.com/find-a-pharmacy/"
        location_name = j.get("store")
        location_type = "<MISSING>"
        street_address = f"{j.get('address')} {j.get('address2')}".replace(
            "None", ""
        ).strip()
        phone = "".join(j.get("phone")).replace("(615) ", "(615)-").strip()
        if phone.find(" ") != -1:
            phone = phone.split(" ")[0].strip()
        state = j.get("state")
        postal = "".join(j.get("zip"))
        if postal.find("-") != -1:
            postal = postal.split("-")[0].strip()
        country_code = "US"
        city = j.get("city")
        store_number = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours = j.get("hours")
        hours = html.fromstring(hours)
        hours_of_operation = (
            " ".join(hours.xpath("//*/text()")).replace("\n", "").strip() or "<MISSING>"
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
