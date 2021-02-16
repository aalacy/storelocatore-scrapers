import csv
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
    headers = {
        "Referer": "https://storelocator.w3apps.co/map.aspx?shop=argotea-2&container=true"
    }
    session = SgRequests()
    r = session.post(
        "https://storelocator.w3apps.co/get_stores2.aspx?shop=argotea-2&all=1",
        headers=headers,
    )
    js = r.json()["location"]
    out = []
    for j in js:
        id = j.get("id")
        url = f"https://storelocator.w3apps.co/get_store_info.aspx?id={id}"
        out.append(url)
    return out


def get_data(url):
    locator_domain = "https://www.argotea.com"
    api_url = url
    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["location"]
    for j in js:
        street_address = f"{j.get('address')} {j.get('address2')}".strip()
        city = "".join(j.get("city")).strip()
        state = "".join(j.get("state")).strip()
        postal = "".join(j.get("zip")).strip()
        page_url = "https://www.argotea.com/apps/store-locator/"
        country_code = "US"
        store_number = "<MISSING>"
        location_name = "".join(j.get("name")).strip()
        phone = "".join(j.get("phone")).strip() or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("long") or "<MISSING>"
        location_type = "<MISSING>"
        hours = "".join(j.get("notes"))
        divs = html.fromstring(hours)
        tmp = []
        days = divs.xpath("//p/text()")
        for d in days:
            d = list(filter(None, [a.strip() for a in d]))
            d = "".join(d)
            tmp.append(d)
        hours_of_operation = " ; ".join(tmp).strip() or "<MISSING>"

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
    with futures.ThreadPoolExecutor(max_workers=1) as executor:
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
