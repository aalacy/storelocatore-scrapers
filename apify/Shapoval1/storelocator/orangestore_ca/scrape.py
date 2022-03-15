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

    locator_domain = "https://orangestore.ca/"

    page_url = "https://orangestore.ca/find-a-store/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.post(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="content-box-content"]')
    for d in div:
        ad = d.xpath(".//p//text()")
        street_address = "".join(ad[0])
        csz = "".join(ad[1]).replace("\n", "").strip()
        city = csz.split(",")[0].strip()
        state = " ".join(csz.split(",")[1].split()[:-2]).strip() or "<MISSING>"
        postal = " ".join(csz.split(",")[1].split()[-2:]).strip()
        country_code = "CA"
        store_number = "<MISSING>"
        location_name = "".join(d.xpath(".//h3/text()"))
        phone = "".join(ad[2]).strip()
        text = "".join(d.xpath(".//a/@href"))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            " ".join(ad[3:]).replace("\n", "").replace("Map", "").strip()
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
