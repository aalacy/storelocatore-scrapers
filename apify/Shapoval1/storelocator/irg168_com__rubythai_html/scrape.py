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

    locator_domain = "https://www.irg168.com/rubythai.html"

    page_url = "https://www.irg168.com/locations.aspx"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    div = tree.xpath('//li[@class="campus"]')
    for d in div:
        location_name = "".join(d.xpath("./text()")).strip()
        location_type = "".join(d.xpath("./preceding-sibling::li[./b][1]//text()"))
        if location_type != "Ruby Thai Kitchen":
            continue
        street_address = "".join(d.xpath(".//following-sibling::li[1]//text()"))
        ad = "".join(d.xpath(".//following-sibling::li[2]//text()"))
        divs = d.xpath("./following-sibling::li[3]")
        phone = "<MISSING>"
        for d in divs:
            if d.xpath("./@class") == "campus":
                break

            text = "".join(d.xpath("./text()")).lower()
            if "tel" in text:
                phone = text.replace("tel", "").replace(":", "").strip()
                break
        state = ad.split(",")[1].split()[0] or "<MISSING>"
        if state.find("NJ") != -1:
            country_code = "US"
        postal = " ".join(ad.split(",")[1].split()[1:]) or "<MISSING>"
        country_code = "CA"
        try:
            if int(postal):
                country_code = "US"
        except ValueError:
            country_code = "CA"
        city = ad.split(",")[0] or "<MISSING>"
        if state.find("NJ") != -1:
            country_code = "US"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
