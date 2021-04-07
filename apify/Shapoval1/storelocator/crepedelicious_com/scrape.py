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

    locator_domain = "https://www.crepedelicious.com/locations/"
    api_url = "https://www.crepedelicious.com/wp-admin/admin-ajax.php?action=store_search&lat=43.823884&lng=-79.48568&max_results=25&search_radius=50&autoload=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:

        page_url = j.get("url") or "https://www.crepedelicious.com/locations/"
        if page_url.find("#test") != -1:
            page_url = "https://www.crepedelicious.com/locations/"
        location_name = (
            "".join(j.get("store")).replace("&#8217;", "`").replace("&#8211;", "-")
        )
        location_type = "<MISSING>"
        street_address = f"{j.get('address')} {j.get('address2')}".strip()
        phone = j.get("phone") or "<MISSING>"
        state = "".join(j.get("state")).strip()
        postal = j.get("zip")
        country_code = j.get("country")
        if country_code != "Canada" and country_code != "USA":
            continue
        city = j.get("city")
        store_number = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = "<MISSING>"
        hours = j.get("hours")

        if hours != "":
            hours = html.fromstring(hours)
            hours_of_operation = (
                " ".join(hours.xpath("//*/text()")).replace("\n", "").strip()
            )
        if hours == "":
            hours_of_operation = "<MISSING>"
        if (
            hours_of_operation == "<MISSING>"
            and page_url != "http://www.crepedelicious.com/locations/"
        ):
            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            hours_of_operation = (
                " ".join(tree.xpath('//div[@class="operation p"]//text()'))
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
