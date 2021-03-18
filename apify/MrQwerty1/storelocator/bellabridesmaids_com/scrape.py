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


def get_hours(page_url):
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    _tmp = []
    hours = tree.xpath("//h5[text()='Hours']/following-sibling::p//text()")
    hours = list(filter(None, [h.strip() for h in hours]))
    for h in hours:
        if "Complimentary" in h or "Dress" in h:
            break
        if ("appointment" in h.lower() and ":" not in h) or "*" in h:
            continue
        if "appointment" in h.lower() and ":" in h:
            h = h.lower().replace("by appointment only", "")
            if h.strip():
                _tmp.append(h.strip())
                continue
        _tmp.append(h)

    return ";".join(_tmp) or "<MISSING>"


def fetch_data():
    out = []
    locator_domain = "https://bellabridesmaids.com/"
    api_url = "https://storelocator.w3apps.co/get_stores2.aspx?shop=bella-bridesmaids-shop&all=1"
    headers = {
        "Referer": "https://storelocator.w3apps.co/map.aspx?shop=bella-bridesmaids-shop&container=false"
    }

    session = SgRequests()
    r = session.post(api_url, headers=headers)
    js = r.json()["location"]

    for j in js:
        street_address = (
            f"{j.get('address')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )

        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("id") or "<MISSING>"
        location_name = j.get("name") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        if "To" in phone:
            phone = "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("long") or "<MISSING>"
        location_type = "<MISSING>"
        page_url = j.get("website") or "<MISSING>"
        hours_of_operation = get_hours(page_url)
        print(page_url, ":", hours_of_operation)

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
