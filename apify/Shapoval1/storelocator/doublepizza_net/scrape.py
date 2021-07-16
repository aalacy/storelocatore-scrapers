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

    locator_domain = "https://www.doublepizza.net"
    api_url = "https://double-pizza-order-online-english.brygid.online/zgrid/themes/13371/portal/index.jsp"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    ll = (
        "["
        + "".join(tree.xpath('//script[contains(text(), "var locations")]/text()'))
        .split("var locations = ")[1]
        .split("'003' ],")[1]
        .split(";")[0]
    )
    li = eval(ll)
    div = tree.xpath('//div[@id="sidebarLocationEntry-manual"]')

    for d, l in zip(div, li):

        page_url = "".join(d.xpath('.//a[@class="location-btn-order"]/@href'))
        location_name = "".join(d.xpath("./b[1]/text()"))
        location_type = "<MISSING>"
        ad = d.xpath("./b[1]/following-sibling::text()")
        ad = list(filter(None, [a.strip() for a in ad]))
        ad = " ".join(ad)
        street_address = " ".join(ad.split(",")[0].split()[:-1])

        state = "".join(ad.split(",")[1]).strip()
        postal = "".join(ad.split(",")[2]).strip()
        country_code = "CA"
        city = "".join(ad.split(",")[0].split()[-1]).strip()
        if city.find("(") != -1:
            city = city.split("(")[0].strip()
        store_number = (
            page_url.split("-")[0].split("store0")[1].replace("0", "").strip()
        )
        hours_of_operation = d.xpath('.//p[@class="location-hours"]/text()')
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation)
        latitude = l[0]
        longitude = l[1]
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        phone = "".join(tree.xpath('//div[./a[contains(@href, "tel")]]/a[1]/text()'))

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
