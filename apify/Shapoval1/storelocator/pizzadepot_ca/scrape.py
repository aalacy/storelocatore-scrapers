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

    locator_domain = "https://www.pizzadepot.ca"
    api_url = "https://www.pizzadepot.ca/location/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)

    slug = tree.xpath('//span[./i[@class="fas fa-home"]]/following-sibling::span')
    for d in slug:
        sg = (
            "".join(d.xpath(".//text()"))
            .replace(",", "")
            .lower()
            .strip()
            .replace(" ", "-")
            .replace("(", "")
            .replace(")", "")
            .strip()
        )

        page_url = f"https://www.pizzadepot.ca/{sg}"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        ad = "".join(tree.xpath('//meta[@property="og:description"]/@content'))

        if ad.find("Hagersville 28") == -1 and ad.find("Vaughan (Wonderland)") == -1:
            ad = ad.split("Depot")[1].split("@")[0].strip()
        if ad.find("Hours") != -1:
            ad = ad.split("Monday")[0].strip()
        ad = " ".join(ad.split()[:-1]).strip()
        if ad.find("Hagersville 28") != -1:
            ad = (
                ad.replace("Hagersville 28", "28")
                .split("hagersville@pizzadepot.ca")[0]
                .strip()
            )
        ad = (
            ad.replace("945 Peter Robertson", "945 Peter Robertson,")
            .replace("4265 Thomas Alton Blvd", "4265 Thomas Alton Blvd,")
            .replace("825 Weber Street E", "825 Weber Street E,")
        )
        if ad.find("Vaughan") != -1:
            ad = "".join(tree.xpath('//iframe[contains(@title, "9461")]/@title'))
        ad = ad.replace("(519) 256", "(519)-256")

        location_type = "<MISSING>"
        street_address = ad.split(",")[0].strip()

        phone = ad.split()[-1].strip()
        if phone.find("Canada") != -1:
            phone = "".join(tree.xpath('//span[contains(text() ,"289-")]/text()'))

        state = "Ontario"
        postal = " ".join(ad.split()[-3:-1]).strip()

        country_code = "Canada"
        city = ad.split(",")[1].split()[0]
        if street_address.find("945") != -1:
            city = "Brampton"
        if street_address.find("4265") != -1:
            city = "Burlington"
        if street_address.find("825") != -1:
            city = "Kitchener"
        if street_address.find("vaughan") != -1:
            city = "Vaughan"
        if street_address.find("3945") != -1:
            city = "Mississauga"
        if street_address.find("9461") != -1:
            street_address = " ".join(street_address.split()[:-1])
            city = "Maple"
        if city.find("Stoney") != -1:
            city = "Stoney Creek"

        location_name = city + " " + "Pizza Depot"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = tree.xpath(
            '//div[./div/h3[contains(text(), "Hours")]]/following-sibling::div//p/text() | //div[./div/h2[contains(text(), "Hours")]]/following-sibling::div//p/text()'
        )
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation) or "<MISSING>"
        if page_url.find("vaughan") != -1:
            hours_of_operation = "Monday-Thursday" + hours_of_operation

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
