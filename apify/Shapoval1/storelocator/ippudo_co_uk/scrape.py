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

    locator_domain = "http://www.ippudo.co.uk"
    page_url = "http://www.ippudo.co.uk/store/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//h3[@class="title center"]')
    for d in div:

        location_name = "".join(d.xpath(".//text()"))
        location_type = "STORE"
        ad = d.xpath(".//following-sibling::table[1]//tr[2]/td/text()")
        ad = list(filter(None, [a.strip() for a in ad]))
        ad = " ".join(ad)
        street_address = (
            " ".join(ad.split()[:-3])
            .replace("Level Minus One Crossrail Station and Retail Mall", "")
            .replace(",", "")
            .replace("  ", " ")
            .strip()
        )
        state = "<MISSING>"
        postal = " ".join(ad.split()[-2:])
        country_code = "UK"
        city = ad.split()[-3].strip()
        store_number = "<MISSING>"
        map_link = "".join(d.xpath(".//following-sibling::div/iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        phone = "".join(d.xpath(".//following-sibling::table[1]//tr[1]/td/text()"))
        hours_of_operation = d.xpath(".//following-sibling::table[1]//tr[3]/td/text()")
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = (
            " ".join(hours_of_operation)
            .replace("(last order 09:30pm)", "")
            .replace("(last order 09:00pm)", "")
            .replace("(last order 08:00pm)", "")
            .replace("(last order 08:30pm)", "")
            .replace("(lase order 09:00pm)", "")
            .replace("  ", " ")
        )
        if hours_of_operation.find("Please") != -1:
            hours_of_operation = hours_of_operation.split("Please")[0].strip()

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
