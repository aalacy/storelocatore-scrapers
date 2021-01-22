import csv

from concurrent import futures
from lxml import html, etree
from sgrequests import SgRequests
from sgzip.static import static_coordinate_list, SearchableCountries


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


def get_data(coord):
    rows = []
    lat, lon = coord
    locator_domain = "https://www.popularbank.com/"

    data = {
        "lat": lat,
        "lng": lon,
        "searchby": "FCS|",
    }

    session = SgRequests()
    r = session.post("http://www.popular.locatorsearch.com/GetItems.aspx", data=data)
    parser = etree.XMLParser(strip_cdata=False)
    root = etree.fromstring(r.content, parser=parser)

    markers = root.xpath("//marker")
    for m in markers:
        page_url = "<MISSING>"
        location_name = "".join(m.xpath(".//title/text()")).split(">")[1].split("<")[0]
        street_address = "".join(m.xpath(".//add1/text()")) or "<MISSING>"
        line = "".join(m.xpath(".//add2/text()"))
        phone = line.split("<b>")[-1].split("<br")[0]
        line = line.split("<br>")[0]
        city = line.split(", ")[0]
        state = line.split(", ")[1].split()[0]
        postal = line.split(", ")[1].split()[1]
        country_code = "US"
        store_number = "<MISSING>"
        latitude = "".join(m.xpath("./@lat")) or "<MISSING>"
        longitude = "".join(m.xpath("./@lng")) or "<MISSING>"
        location_type = "<MISSING>"

        t = "".join(m.xpath(".//contents/text()"))
        tree = html.fromstring(t)
        text = tree.xpath("//p//text()")[2:]
        hours_of_operation = (
            "".join(text)
            .replace(
                "Drive-thru service only. To meet with a banker please call to make an appointment.",
                "",
            )
            .replace("\n", ";")
        )

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

        rows.append(row)

    return rows


def fetch_data():
    out = []
    s = set()
    coords = static_coordinate_list(radius=200, country_code=SearchableCountries.USA)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, coord): coord for coord in coords}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                _id = tuple(row[2:6])
                if _id not in s:
                    s.add(_id)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
