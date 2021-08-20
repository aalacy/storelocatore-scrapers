import csv
from sgscrape.sgpostal import International_Parser, parse_address
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


def get_data():
    out = []
    locator_domain = "https://www.timex.com"
    session = SgRequests()

    r = session.get("https://www.timex.com/stores-find")
    tree = html.fromstring(r.text)
    url = "".join(tree.xpath("//form[@id='dwfrm_storelocator_state']/@action"))
    states = tree.xpath("//select[@id='dwfrm_storelocator_state']/option/@value")[1:]

    for state in states:

        data = {
            "dwfrm_storelocator_state": state,
            "dwfrm_storelocator_findbystate": "Search",
        }

        r = session.post(url, data=data)
        tree = html.fromstring(r.text)
        tr = tree.xpath('//table[@class="item-list"]/tbody/tr')
        for t in tr:

            location_name = (
                "".join(t.xpath('.//div[@class="store-name"]/text()'))
                .replace("\n", "")
                .replace("()", "")
                .strip()
                or "<MISSING>"
            )
            text = (
                " ".join(t.xpath('.//td[@class="store-address"]/text()'))
                .replace("\n", "")
                .strip()
            )
            a = parse_address(International_Parser(), text)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            city = a.city
            state = a.state
            postal = a.postcode
            country_code = "US"
            hours_of_operation = (
                " ".join(t.xpath('.//div[@class="store-hours"]/p/text()')).replace(
                    "\n", ""
                )
                or "<MISSING>"
            )
            store_number = "<MISSING>"
            phone = "<MISSING>"
            slug = "".join(t.xpath('.//div[@class="store-name"]/a/@href'))
            page_url = f"https://www.timex.com{slug}"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            location_type = "<MISSING>"

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
    data = get_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
