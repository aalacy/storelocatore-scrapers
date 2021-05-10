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


def get_hours(url):
    _tmp = []
    session = SgRequests()
    r = session.get(url)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[@class='location__hours__container']/div[last()]/div[contains(@class, 'location__hours__day')]"
    )

    for d in divs:
        day = "".join(d.xpath("./span[1]//text()")).strip()
        time = "".join(d.xpath("./span[2]//text()")).strip()
        _tmp.append(f"{day}: {time}")

    return ";".join(_tmp) or "<MISSING>"


def fetch_data():
    out = []
    locator_domain = "https://smartstopselfstorage.com/"
    api_url = "https://smartstopselfstorage.com/umbraco/rhythm/locationsapi/findlocations?size=&latitude=36.563752659280766&longitude=-73.941626814556&radius=3915.6025249727622&culture=en-us"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["items"]

    for j in js:
        street_address = j.get("address1") or "<MISSING>"
        csz = j.get("address2")
        city = csz.split(",")[0].strip()
        csz = csz.split(",")[1].strip()
        state = csz.split()[0]
        if state == "ONT":
            state = "ON"
        postal = csz.split(state)[1].replace("T ", "").strip()
        if len(postal) == 5:
            country_code = "US"
        else:
            country_code = "CA"
        store_number = "<MISSING>"
        slug = j.get("url") or ""
        page_url = f"https://smartstopselfstorage.com{slug}"
        location_name = f"Self Storage in {city} {state}"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = get_hours(page_url)

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
