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


def fetch_data():
    out = []
    locator_domain = "https://www.worknetoccupationalmedicine.com/"
    page_url = "https://www.worknetoccupationalmedicine.com/find-a-location/#g=&o=Distance,Ascending"
    api_url = "https://www.worknetoccupationalmedicine.com//sxa/search/results/?s={47229739-6FFF-4802-8CC0-D4EB1BD20866}|{47229739-6FFF-4802-8CC0-D4EB1BD20866}&itemid={02D546B1-BD74-4AF5-8416-D0E61C36DD70}&sig=&v=%7B55BD26AB-5DEC-4454-9214-5C9AEA0EF752%7D&p=20&g=&o=Distance%2CAscending"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["Results"]

    for j in js:
        text = j.get("Html")
        tree = html.fromstring(text)
        line = tree.xpath("//div[@class='loc-result-card-address-container']//a/text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = line[0] or "<MISSING>"
        if len(line[:-1]) >= 2:
            if line[1].lower().find("suite") != -1:
                street_address += f", {line[1]}"
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.replace(state, "").strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_name = "".join(
            tree.xpath("//div[@class='loc-result-card-name']/text()")
        ).strip()
        phone = tree.xpath("//a[contains(@href, 'tel')]/text()")[0]
        loc = j.get("Geospatial")
        latitude = loc.get("Latitude") or "<MISSING>"
        longitude = loc.get("Longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        tr = tree.xpath("//tr")
        for t in tr:
            day = "".join(t.xpath("./td[1]/text()")).strip()
            time = "".join(t.xpath("./td[2]/text()")).strip()
            _tmp.append(f"{day} {time}")

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
