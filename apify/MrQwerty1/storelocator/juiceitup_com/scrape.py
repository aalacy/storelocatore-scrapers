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


def get_hours(url):
    _id = url[0]
    url = url[1]
    data = {"_m_": "HoursPopup", "HoursPopup$_edit_": _id, "HoursPopup$_command_": ""}

    session = SgRequests()
    r = session.post(url, data=data)
    tree = html.fromstring(r.text)

    _tmp = []
    hours = tree.xpath("//tr")
    for h in hours:
        day = "".join(h.xpath("./td[1]/text()")).strip()
        time = "".join(h.xpath("./td[2]//text()")).strip()
        _tmp.append(f"{day}: {time}")

    hoo = ";".join(_tmp) or "<MISSING>"
    if hoo.count("Closed") == 7:
        hoo = "Closed"

    return {_id: hoo}


def fetch_data():
    out = []
    urls = []
    hours = []
    session = SgRequests()
    locator_domain = "https://www.juiceitup.com/"
    r = session.get("https://www.juiceitup.com/stores/?CallAjax=GetLocations")
    js = r.json()

    for j in js:
        urls.append(
            [j.get("FranchiseLocationID"), "https://www.juiceitup.com" + j.get("Path")]
        )

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_hours, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            hours.append(future.result())

    hours = {k: v for elem in hours for (k, v) in elem.items()}

    for j in js:
        page_url = "https://www.juiceitup.com" + j.get("Path")
        _id = j.get("FranchiseLocationID")
        location_name = j.get("BusinessName")
        street_address = (
            f'{j.get("Address1")} {j.get("Address2") or ""}'.strip() or "<MISSING>"
        )
        city = j.get("City") or "<MISSING>"
        state = j.get("State") or "<MISSING>"
        postal = j.get("ZipCode") or "<MISSING>"
        country_code = "US"
        store_number = _id
        phone = j.get("Phone") or "<MISSING>"

        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
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
