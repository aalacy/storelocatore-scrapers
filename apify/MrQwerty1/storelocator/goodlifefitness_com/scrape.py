import csv

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


def get_urls():
    session = SgRequests()
    r = session.get("https://www.goodlifefitness.com/sitemap.xml")
    tree = html.fromstring(r.content)
    return tree.xpath("//loc[contains(text(), 'clubs/club.')]/text()")


def get_data(page_url):
    session = SgRequests()
    _id = page_url.split(".")[-2]
    r = session.get(
        f"https://www.goodlifefitness.com/content/experience-fragments/goodlife/header/master/jcr:content"
        f"/root/responsivegrid/header.GetClubsWithDetails.{_id}.false.true.20201022.json"
    )

    # non-exist pages return status code 204
    if r.status_code != 200:
        return

    j = r.json()["map"]["response"][0]
    locator_domain = "https://www.goodlifefitness.com/"
    location_name = j.get("ClubName") or "<MISSING>"
    street_address = j.get("Address1") or "<MISSING>"
    city = j.get("City") or "<MISSING>"
    state = j.get("Province") or "<MISSING>"
    postal = j.get("PostalCode")
    country_code = "CA"
    store_number = _id
    phone = j.get("Phone") or "<MISSING>"
    location_type = "<MISSING>"
    latitude = j.get("Lat") or "<MISSING>"
    longitude = j.get("Long") or "<MISSING>"

    _tmp = []
    days = [
        "sunday",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
    ]
    hours = j.get("OperatingHours") or []

    for h in hours:
        day = days[h.get("Day")]
        start = h.get("StartTime").split("T")[1][:-3]
        end = h.get("EndTime").split("T")[1][:-3]
        if start.find("00:00") == -1:
            _tmp.append(f"{day.capitalize()}: {start} - {end}")
        else:
            _tmp.append(f"{day.capitalize()}: Closed")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
