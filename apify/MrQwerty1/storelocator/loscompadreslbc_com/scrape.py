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


def get_coords_from_google_url(url):
    try:
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_hours():
    hours = []
    session = SgRequests()
    r = session.get("http://loscompadreslbc.com/")
    tree = html.fromstring(r.text)
    tr = tree.xpath("//table//tr")[1:]

    for i in range(2, 5):
        _tmp = []
        for t in tr:
            day = "".join(t.xpath("./td[1]/h5/strong/text()")).strip()
            time = "".join(t.xpath(f"./td[{i}]/h5/strong/text()")).strip()
            _tmp.append(f"{day}: {time}")
        hours.append(";".join(_tmp) or "<MISSING>")

    return hours


def fetch_data():
    out = []
    cnt = 0
    locator_domain = "http://loscompadreslbc.com/"
    page_url = "http://loscompadreslbc.com/services/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    hours = get_hours()
    divs = tree.xpath("//div[contains(@class, 'panel-grid-cell') and .//img]")

    for d in divs:
        line = d.xpath(".//p/text()")
        line = list(filter(None, [l.strip() for l in line]))

        street_address = line[0].replace("\u2028", "")
        phone = line[-1]
        line = line[1].replace(",", "")
        postal = line.split()[-1]
        state = line.split()[-2]
        city = line.replace(postal, "").replace(state, "").strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_name = "".join(d.xpath(".//p/strong/text()")).strip()

        text = "".join(d.xpath(".//p/a[contains(@href, 'map')]/@href"))
        latitude, longitude = get_coords_from_google_url(text)
        location_type = "<MISSING>"
        hours_of_operation = hours[cnt]

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
        cnt += 1

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
