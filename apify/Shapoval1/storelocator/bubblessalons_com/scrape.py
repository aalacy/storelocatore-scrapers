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
    locator_domain = "http://www.bubblessalons.com"
    api_url = "http://www.bubblessalons.com/api/content/render/false/type/xml/query/+structureName:BubblesSalonLocations%20+(conhost:48190c8c-42c4-46af-8d1a-0cd5db894797%20conhost:SYSTEM_HOST)%20+languageId:1*%20+deleted:false%20+live:true%20%20+working:true/orderby/modDate%20desc/limit/50"
    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.content)
    for i in tree:
        location_name = "".join(i.xpath(".//title/text()"))
        street_address = "".join(i.xpath(".//address/text()"))
        phone = "".join(i.xpath(".//phone/text()"))
        city = "".join(i.xpath(".//city/text()"))

        state = "".join(i.xpath(".//state/text()"))
        country_code = "US"
        store_number = "<MISSING>"
        latitude = "".join(i.xpath(".//latitude/text()"))
        longitude = "".join(i.xpath(".//longitude/text()"))
        location_type = "<MISSING>"
        hours_of_operation = (
            "".join(i.xpath('.//*[contains(text(), "pm")]/text()'))
            .replace("{", "")
            .replace("}", "")
            .strip()
        )
        page_url = "http://www.bubblessalons.com" + "".join(
            i.xpath('.//*[contains(text(), "/find-a-bubbles-salon/")]/text()')
        )
        session = SgRequests()
        r = session.get(page_url)
        trees = html.fromstring(r.text)
        ad = trees.xpath('//div[@class="adress"]//text()')
        ad = list(filter(None, [a.strip() for a in ad]))
        ad = " ".join(ad)
        postal = ad.split()[-1]
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
