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
    _tmp = []
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    pp = tree.xpath("//p[.//text()='OPENING HOURS']/following-sibling::p//text()")
    for p in pp:
        if p.find("Bank") != -1:
            break
        _tmp.append(p.strip())

    return ";".join(_tmp) or "<MISSING>"


def fetch_data():
    out = []
    locator_domain = "https://www.petsandfriends.co.uk/"
    api_url = (
        "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/8586/stores"
    )

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["stores"]

    for j in js:
        line = j.get("address").split(",")

        if line[-1].strip() == "UK":
            line = line[:-1]
            street_address = line[0].strip()
            city = line[-2].strip()
            state = " ".join(line[-1].split()[:-2]).strip()
            postal = " ".join(line[-1].split()[-2:]).strip()
        else:
            street_address = ", ".join(line[:-3]).strip()
            city = line[-3].strip()
            state = line[-2].strip()
            postal = line[-1].strip()

        if street_address == city:
            city = "<MISSING>"
        country_code = "GB"
        store_number = "<MISSING>"
        page_url = j.get("url") or "<MISSING>"
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        if page_url != "<MISSING>":
            hours_of_operation = get_hours(page_url)
        else:
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
