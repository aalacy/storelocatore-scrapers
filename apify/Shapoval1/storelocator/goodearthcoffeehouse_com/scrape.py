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
    locator_domain = "https://goodearthcoffeehouse.com"
    api_url = "https://goodearthcoffeehouse.com/locations/"
    session = SgRequests()

    r = session.get(api_url)
    tree = html.fromstring(r.text)
    block = tree.xpath('//select[@name="city"]/optgroup/option')
    for i in block:
        slug = "".join(i.xpath(".//text()"))
        if slug.find(" ") != -1:
            slug = slug.replace(" ", "-")

        page_url = f"{api_url}{slug}".replace("St.", "st").lower()
        if page_url.find("banff") != -1:
            page_url = f"{api_url}{slug}".replace("St.", "st")
        if page_url.find("north-vancouver") != -1:
            page_url = f"{api_url}north-van"
        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="scroller"]/div[contains(@class, "location")]')
        for d in div:
            location_name = "".join(d.xpath(".//h3/text()"))
            ad = d.xpath(".//h3/following-sibling::p[1]/text()")

            street_address = "".join(ad[0]).replace("\n", "").strip()
            locality = "".join(ad[1]).replace("\n", "").strip()
            city = locality.split(",")[0].strip()
            state = locality.split(",")[1].strip()
            postal = locality.split(",")[2].strip()
            phone = "<MISSING>"
            if len(ad) == 3:
                phone = "".join(ad[2]).replace("\n", "").strip()
            if phone == "":
                phone = "<MISSING>"
            country_code = "CA"
            store_number = "<MISSING>"
            latitude = "".join(d.xpath(".//@data-lat"))
            longitude = "".join(d.xpath(".//@data-long"))
            location_type = "<MISSING>"
            hours_of_operation = d.xpath('.//p[@class="location-hours"]/text()')
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = (
                "".join(hours_of_operation).replace("\r", "").replace("\n", "")
                or "<MISSING>"
            )
            if hours_of_operation.find("CURB") != -1:
                hours_of_operation = hours_of_operation.split("CURB")[0].strip()
            if (
                hours_of_operation.find("Holiday") != -1
                or hours_of_operation.find("RE-OPENING") != -1
                or hours_of_operation.find("Opening") != -1
            ):
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
