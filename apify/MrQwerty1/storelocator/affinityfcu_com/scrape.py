import csv

from lxml import html, etree
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
    locator_domain = "https://www.affinityfcu.com/"
    page_url = "https://www.affinityfcu.com/locations/index.aspx"
    api = "https://joinaffinity.locatorsearch.com/GetItems.aspx"

    data = {
        "lat": "40.858611203801",
        "lng": "-73.88931",
        "searchby": "FCS|",
        "SearchKey": "",
        "rnd": "1625926008507",
    }

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.post(api, headers=headers, data=data)
    tree = etree.fromstring(r.content)
    divs = tree.xpath("//marker")

    for d in divs:
        text = "".join(d.xpath(".//title/text()")).strip()
        location_name = "Affinity Federal Credit Union"
        store_number = text.split("Loc=")[1].split('"')[0]

        street_address = (
            "".join(d.xpath(".//add1/text()")).replace("</br>", ", ").strip()
        )
        add2 = "".join(d.xpath(".//add2/text()")).strip()
        city = add2.split(",")[0].strip()
        add2 = add2.split(",")[1].strip()
        state = add2.split()[0]
        postal = add2.split()[1].split("<")[0]
        phone = (
            add2.split("<b>")[-1]
            .split("<")[0]
            .replace("Restricted Access", "<MISSING>")
        )
        country_code = "US"
        latitude = "".join(d.xpath("./@lat")) or "<MISSING>"
        longitude = "".join(d.xpath("./@lng")) or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        text = "".join(d.xpath(".//contents/text()"))
        root = html.fromstring(text)
        tr = root.xpath("//tr")
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
