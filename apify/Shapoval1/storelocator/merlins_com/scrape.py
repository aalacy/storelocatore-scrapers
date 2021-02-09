import csv
import json

from lxml import html
from sgrequests import SgRequests
from concurrent import futures


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


def get_urls():
    session = SgRequests()
    ur = []
    api_url = "https://api.merlins.com/api/stores/"
    r = session.get(api_url)
    js = json.loads(r.text)["message"]["stores"]
    for j in js:
        store_number = j.get("storeId")
        ur.append(store_number)
    return ur


def get_data(url):
    locator_domain = "https://www.merlins.com/"
    api_url = f"https://api.merlins.com/api/store/{url}"
    session = SgRequests()
    r = session.get(api_url)
    js = json.loads(r.text)["message"]
    for j in js:
        store_number = j.get("storeId")
        street_address = (
            f"{j.get('streetAddress1')} {j.get('streetAddress2')}" or "<MISSING>"
        )
        city = "".join(j.get("locationCity"))
        state = "".join(j.get("locationState"))
        postal = j.get("locationPostalCode")
        country_code = "US"
        page_url = j.get("storeURL") or "<MISSING>"
        if page_url.find("plainfieldsouth") != -1:
            page_url = f"https://www.merlins.com/locations/{state.lower()}/{city.lower()}-{store_number}"
        if page_url.find("plainfieldnorth") != -1:
            page_url = f"https://www.merlins.com/locations/{state.lower()}/{city.lower()}-{store_number}"
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = "<MISSING>"
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        text = tree.xpath('///div[@class="centerinfo-hours"]')
        location_name_text = tree.xpath('///div[@class="centerinfo-general"]')
        titles = []
        for l in location_name_text:
            title = "".join(l.xpath("./h1/text()"))
            titles.append(title)
        location_name = "".join(titles) or "<MISSING>"
        for t in text:
            hours = t.xpath("./p[position()>1]")
            times = []
            for h in hours:
                day = "".join(h.xpath("./strong/text()"))
                time = "".join(h.xpath("text()"))
                line = f"{day} - {time}".replace("\xa0 - ", "")
                times.append(line)
            hours_of_operation = "|".join(times) or "<MISSING>"

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

        return row


def fetch_data():
    out = []
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
