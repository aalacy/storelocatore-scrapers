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
    locator_domain = "https://emackandbolios.com"
    page_url = "https://emackandbolios.com/locations/"
    location_type = "<MISSING>"
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[./div/h2[contains(text(), "New York")]]/following-sibling::section/div/div/div[.//p] | //div[./div/h2[contains(text(), "New York")]]/following-sibling::section/div/div/div[.//span]'
    )
    for d in div:

        street_address = "<MISSING>"
        phone = "<MISSING>"
        city = "<MISSING>"
        postal = "<MISSING>"
        state = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        location_name = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"
        ad = d.xpath(".//text()")
        ad = list(filter(None, [a.strip() for a in ad]))
        if len(ad) == 5:
            location_name = "".join(ad[0]).strip()
            street_address = "".join(ad[1]).strip()
            city = "".join(ad[2]).split(",")[0].strip()
            state = "".join(ad[2]).split(",")[1].strip()
            phone = "".join(ad[3]).strip()
        if len(ad) == 4 and "".join(ad).find("Hard") == -1:
            location_name = "".join(ad[0]).strip()
            street_address = "".join(ad[1]).strip()
            city = "".join(ad[2]).split(",")[0].strip()
            state = "".join(ad[2]).split(",")[1].strip()
            phone = "".join(ad[3]).strip()
        if "".join(ad).find("Las Vegas") != -1:
            city = "".join(ad[0])
            street_address = "".join(ad[1])
        if "".join(ad).find("Upper Darby") != -1:
            city = "".join(ad[1]).split(",")[0].strip()
            state = "".join(ad[1]).split(",")[1].strip()
            hours_of_operation = "".join(ad[0])
        if "".join(ad).find("Aventura") != -1:
            location_name = "".join(ad[0])
            city = "".join(ad[1]).split(",")[0].strip()
            state = "".join(ad[1]).split(",")[1].strip()
        if location_name.find("Midtown") != -1:
            phone = "<MISSING>"
        if location_name.find("Coming") != -1:
            phone = "<MISSING>"
            hours_of_operation = "".join(ad[0])
            location_name = "".join(ad[1])
            street_address = "<MISSING>"
        if "".join(ad).find("Hard") != -1:
            location_name = "".join(ad[0]).strip()
            city = "".join(ad[1]).split(",")[0].strip()
            state = "".join(ad[1]).split(",")[1].strip()
            phone = "".join(ad[2]).strip()

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
