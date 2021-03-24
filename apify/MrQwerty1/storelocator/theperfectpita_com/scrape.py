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


def get_map_from_google_url(url):
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


def fetch_data():
    out = []
    locator_domain = "https://theperfectpita.com/"
    page_url = "https://theperfectpita.com/locations/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[@class='et_pb_text_inner' and ./h6 and not(.//img[contains(@src, 'permnantly_closed')])]"
    )

    for d in divs:
        location_name = "".join(d.xpath("./h6/text()")).strip()
        line = d.xpath("./p[1]/text()")
        line = list(filter(None, [l.strip() for l in line]))

        street_address = ", ".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        try:
            postal = line.split()[1]
        except IndexError:
            postal = "<MISSING>"

        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(d.xpath("./p[2]/strong[1]/text()"))
            .replace("PITA", "")
            .replace("(", "")
            .replace(")", "")
            .replace(" ", "")
        )
        text = "".join(d.xpath(".//a[contains(@href, 'google')]/@href"))
        latitude, longitude = get_map_from_google_url(text)
        location_type = "<MISSING>"

        _tmp = []
        for p in d.xpath("./p")[1:]:
            line = p.xpath(".//text()")
            text = " ".join(line)
            if text.lower().find("regular") != -1:
                for l in line:
                    if "-" in l:
                        _tmp.append(l)
                break

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
