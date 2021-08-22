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

    locator_domain = "https://www.theainsworth.com"
    api_url = "https://www.theainsworth.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[@data-current-styles]//following::div[@class="container header-menu-nav-item"]/a'
    )

    for d in div:
        slug = "".join(d.xpath(".//@href"))
        if slug.find("locations") != -1:
            continue

        page_url = f"{locator_domain}{slug}"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1/text()"))
        ad = tree.xpath("//h1/following-sibling::*//text()")
        adr = "".join(ad[0]).strip()
        if "".join(ad).find("NOW OPEN!") != -1:
            adr = "".join(ad[1]).strip()
        if "".join(ad).find("COMING SOON") != -1:
            adr = "<MISSING>"
        adr = adr.replace("Rockville Centre", ",Rockville Centre").strip()
        location_type = "<MISSING>"
        street_address = "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"
        country_code = "USA"
        city = "<MISSING>"

        if adr != "<MISSING>":
            street_address = adr.split(",")[0].strip()
            city = adr.split(",")[1].strip()
            state = adr.split(",")[2].split()[0].strip()
            postal = adr.split(",")[2].split()[1].strip()

        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        phone = (
            "".join(tree.xpath("//h1/following-sibling::p[./a]/a/text()"))
            or "<MISSING>"
        )
        if phone == "<MISSING>":
            phone = (
                "".join(tree.xpath("//h1/following-sibling::p/text()")) or "<MISSING>"
            )
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="image-subtitle-wrapper"]//p/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )

        if "".join(ad).find("TEMPORARILY CLOSED") != -1:
            hours_of_operation = "Temporarily Closed"
        if "".join(ad).find("COMING SOON") != -1:
            hours_of_operation = "Coming Soon"

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
