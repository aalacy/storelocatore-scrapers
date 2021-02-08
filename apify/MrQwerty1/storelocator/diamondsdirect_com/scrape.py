import csv
import re

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
    locator_domain = "https://diamondsdirect.com/"
    api_url = "https://diamondsdirect.com/assets/bundle-2056.js"

    session = SgRequests()
    r = session.get(api_url)
    text = r.text
    text = text.split(
        't.default=x;t.TeamModalContainer=(0,p.connect)(l,w)(x)},function(e,t){"use strict";Object.defineProperty(t,"__esModule",{value:!0});'
    )[1].split(";t.ALL={")[0]
    for t in text.split("={")[1:]:
        if t.find('"store"') == -1:
            continue

        t = t.split(",team:")[0]
        slug = (
            "".join(re.findall(r'shortName:"(.*?)"', t))
            .lower()
            .replace(" ", "-")
            .replace(".", "")
        )
        page_url = f"https://diamondsdirect.com/{slug}"
        street_address = "".join(re.findall(r'line1:"(.*?)"', t)) or "<MISSING>"
        if street_address.find("196 E Winchester") != -1:
            continue
        line = "".join(re.findall(r'line2:"(.*?)"', t))
        city = line.split(",")[0].strip()
        line = line.split(",")[-1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = "<MISSING>"
        location_name = "".join(re.findall(r'name:"(.*?)"', t))
        phone = "".join(re.findall(r'phone:"(.*?)"', t))
        loc = "".join(re.findall(r'googleMapsLink:"(.*?)"', t))
        try:
            if loc.find("ll=") != -1:
                latitude = loc.split("ll=")[1].split(",")[0]
                longitude = loc.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = loc.split("@")[1].split(",")[0]
                longitude = loc.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours_text = t.split("default:")[1].split(",holiday:")[0]
        days = re.findall(r'days:"(.*?)"', hours_text)
        times = re.findall(r'hours:"(.*?)"', hours_text)

        for day, time in zip(days, times):
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
