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

    locator_domain = "https://www.zippys.com"
    api_url = "https://www.zippys.com/wp-admin/admin-ajax.php?action=store_search&lat=21.30694&lng=-157.85833&max_results=10&search_radius=50&autoload=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": "https://www.zippys.com/locations/",
        "TE": "Trailers",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:

        page_url = j.get("permalink")
        location_name = "".join(j.get("store")).replace("&#8217;", "`").strip()
        location_type = "Restaurant"
        street_address = f"{j.get('address')} {j.get('address2')}".strip()
        state = j.get("state")
        postal = j.get("zip")
        country_code = j.get("country")
        city = j.get("city")
        store_number = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        phone = j.get("phone")
        _tmp = []
        hours_of_operation = j.get("hours") or "<MISSING>"
        if hours_of_operation != "<MISSING>":
            h = html.fromstring(hours_of_operation)
            days = h.xpath("//td/text()")
            times = h.xpath("//td/time[2]/text()")
            for d, t in zip(days, times):
                _tmp.append(f"{d.strip()}: {t.strip()}")
            hours_of_operation = ";".join(_tmp)
        if (
            page_url == "https://www.zippys.com/locations/zippys-pearlridge/"
            and hours_of_operation == "<MISSING>"
        ):
            hours_of_operation = "Closed"
        if (
            page_url == "https://www.zippys.com/locations/zippys-waimalu/"
            and hours_of_operation == "<MISSING>"
        ):
            hours_of_operation = "Temporarily closed"

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
