import csv
import json
from sgrequests import SgRequests
from lxml import html


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
    locator_domain = "http://www.haroldschickenscorp.com"
    page_url = "http://www.haroldschickenscorp.com/locations/"

    session = SgRequests()
    r = session.get(page_url)
    block = r.text.split("var LocationDataUS = ")[1].split(";")[0]
    js = json.loads(json.dumps(eval(block)))
    for j in js:
        line = j[0]
        line = html.fromstring(line)
        ad = line.xpath("//text()")
        street_address = "".join(ad[1])
        city = " ".join("".join(ad[2]).split()[:-1])
        postal = "<MISSING>"
        state = "".join(ad[2]).split()[-1]
        country_code = "US"
        store_number = "<MISSING>"
        location_name = "".join(ad[0])
        if location_name.find("#") != -1:
            store_number = location_name.split("#")[1].strip()
            if store_number.find("b") != -1:
                store_number = store_number.split("b")[0].strip()
        phone = "".join(ad[3]).strip()
        if street_address.find("600") != -1:
            street_address = "".join(ad[1]) + "".join(ad[2]).strip()
            city = " ".join("".join(ad[3]).split()[:-1]).strip()
            state = "".join("".join(ad[3]).split()[-1]).strip()
            phone = "".join(ad[4]).strip()
        if street_address.find("13801") != -1:
            street_address = "".join(ad[1]) + "".join(ad[2]).strip()
            city = " ".join("".join(ad[3]).split()[:-1]).strip()
            state = "".join("".join(ad[3]).split()[-1]).strip()
            phone = "".join(ad[4]).strip()
        if street_address.find("101") != -1:
            street_address = "".join(ad[1]) + "".join(ad[2]).strip()
            city = " ".join("".join(ad[3]).split()[:-1]).strip()
            state = "".join("".join(ad[3]).split()[-1]).strip()
            phone = "".join(ad[4]).strip()
        latitude = j[1]
        longitude = j[2]
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
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
