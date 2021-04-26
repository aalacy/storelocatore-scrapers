import csv
import re
import json

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


def striphtml(data):
    p = re.compile(r"<.*?>")
    return p.sub("", data)


def fetch_data():
    out = []
    locator_domain = "https://www.pharmachoice.com/"
    api_url = "https://www.pharmachoice.com/locator/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'var bhStoreLocatorLocations')]/text()")
    )
    text = striphtml(
        text.split('var bhStoreLocatorLocations = "')[1]
        .split(']";')[0]
        .replace("\\", "")
    )
    tt = text.split("},{")

    for t in tt:
        t = t.replace("[", "").split('"flyer_plan"')[0][:-1].split('"flyer"')[0]
        if t.endswith(","):
            t = t[:-1]
        if not t.startswith("{"):
            t = "{" + t
        if not t.endswith("}"):
            t += "}"
        if '"id"' not in t:
            continue

        j = json.loads(t)
        location_name = (
            j.get("name")
            .replace("&#8217;", "'")
            .replace("&#038;", "&")
            .replace("&#8211;", "-")
        )
        page_url = j.get("permalink") or "<MISSING>"
        street_address = (
            f"{j.get('address')} {j.get('address2') or ''}".replace(
                "&#39;", "'"
            ).strip()
            or "<MISSING>"
        )
        city = j.get("city").replace("&#39;", "'") or "<MISSING>"
        state = j.get("state").replace("&#39;", "'") or "<MISSING>"
        postal = j.get("postal") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        store_number = j.get("store_number") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        for i in range(1, 8):
            day = days[i - 1]
            time = j.get(f"hours{i}")
            if not time or "TBD" in time:
                continue
            _tmp.append(f"{day}: {time}")

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
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
