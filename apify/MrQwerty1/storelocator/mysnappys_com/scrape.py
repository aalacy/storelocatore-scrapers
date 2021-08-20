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
    locator_domain = "http://www.mysnappys.com/"
    page_url = "http://www.mysnappys.com/locations"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@data-testid='mesh-container-content']/div[./h6 and .//a]")

    for d in divs:
        index = 0
        line = d.xpath(".//text()")
        line = list(filter(None, [l.replace("\u200b", "").strip() for l in line]))
        for li in line:
            if li == "Get Directions":
                break
            index += 1

        phone = line[index - 1]
        csz = line[index - 2].replace(",", "")
        street_address = line[index - 3]
        location_name = " ".join(line[: index - 3])

        postal = csz.split()[-1]
        state = csz.split()[-2]
        city = csz.replace(postal, "").replace(state, "").strip()
        country_code = "US"
        if "#" in location_name:
            store_number = location_name.split("#")[-1].strip()
        else:
            store_number = "<MISSING>"

        text = "".join(d.xpath(".//a[contains(@href, 'maps')]/@href")).replace(
            "%20", ""
        )
        latitude, longitude = eval(text.split("=")[-1])
        location_type = "<MISSING>"
        hours_of_operation = (
            "".join(line[index:]).split("Hours:")[-1].replace("pm", "pm;").strip()
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
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
