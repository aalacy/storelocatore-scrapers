import csv
import json

from concurrent import futures
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


def get_hours(url):
    _id = url.split("/")[-2]
    session = SgRequests()
    r = session.get(url)
    tree = html.fromstring(r.text)
    hours = (
        ";".join(
            tree.xpath("//p[./span/i[@class='icon icon-office-hours']]/text()")
        ).strip()
        or "<MISSING>"
    )

    if hours.find("(") != -1:
        hours = hours.replace("(Production)", "").split("(")[0].strip()

    if hours.find("Production") != -1:
        hours = hours.split(";Production")[0].replace("Walk-in", "").strip()
    elif hours.find("RIOT") != -1:
        hours = hours.split(";RIOT")[0].replace("ARC Repro is open", "").strip()

    return {_id: hours}


def fetch_data():
    out = []
    urls = []
    hours = []
    session = SgRequests()
    locator_domain = "https://www.e-arc.com"
    r = session.get("https://www.e-arc.com/location/")
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'var servicecenters')]/text()")
    )
    text = (
        text.split("var servicecenters = ")[1]
        .split("var $result")[0]
        .replace("];", "")
        .strip()[:-1]
        + "]"
    )
    js = json.loads(text)

    for j in js:
        j = j.get("servicecenter")
        country = j.get("country_name")
        if country == "Canada" or country == "United States":
            urls.append(j.get("permalink"))

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_hours, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            hours.append(future.result())

    hours = {k: v for elem in hours for (k, v) in elem.items()}

    for j in js:
        j = j.get("servicecenter")
        page_url = j.get("permalink") or "<MISSING>"
        _id = page_url.split("/")[-2]
        location_name = j.get("title")
        street_address = j.get("street_address") or "<MISSING>"
        if street_address.find("<br>") != -1:
            street_address = street_address.split("<br>")[-1]
        elif street_address.find("(") != -1:
            street_address = street_address.split("(")[0].strip()
        city = j.get("city") or "<MISSING>"
        state = j.get("province") or "<MISSING>"
        postal = j.get("postalcodes") or "<MISSING>"
        country = j.get("country_name") or "<MISSING>"
        if country == "United States":
            country_code = "US"
        elif country == "Canada":
            country_code = "CA"
        else:
            continue
        store_number = "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        if phone.find("/") != -1:
            phone = phone.replace("(Production)", "").split("/")[0].strip()
        elif phone.find(" or ") != -1:
            phone = phone.split(" or ")[0].strip()
        elif phone.find(" - ") != -1:
            phone = phone.split(" - ")[0].strip()
        elif phone == "<MISSING>":
            phone = j.get("fax") or "<MISSING>"

        latitude = j.get("location_latitude") or "<MISSING>"
        longitude = j.get("location_longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = hours.get(_id)

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
