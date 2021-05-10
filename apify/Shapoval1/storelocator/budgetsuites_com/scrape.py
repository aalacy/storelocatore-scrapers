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

    locator_domain = "https://budgetsuites.com"
    api_url = "https://budgetsuites.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="form-group"]')

    for d in div:
        slug = "".join(d.xpath(".//label/@for"))
        session = SgRequests()
        r = session.get(
            f"https://budgetsuites.com/locations_select.php?name={slug}",
            headers=headers,
        )
        tree = html.fromstring(r.text)
        divs = tree.xpath('//h4[@class="card-title"]')
        for k in divs:
            page_url = "https:" + "".join(k.xpath(".//a/@href"))
            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)

            location_name = "".join(tree.xpath("//h1/b/text()")).split("the")[1].strip()
            location_type = "<MISSING>"
            street_address = "".join(
                tree.xpath('//div[@class="col col-md-5"]/p[3]/text()[1]')
            )
            ad = (
                "".join(tree.xpath('//div[@class="col col-md-5"]/p[3]/text()[2]'))
                .replace("\n", "")
                .strip()
            )
            phone = (
                "".join(tree.xpath('//div[@class="col col-md-5"]/p[3]/text()[3]'))
                .replace("\n", "")
                .strip()
            )
            state = ad.split(",")[1].split()[0].strip()
            postal = ad.split(",")[1].split()[-1].strip()
            country_code = "US"
            city = ad.split(",")[0].strip()
            store_number = "<MISSING>"
            latitude = (
                "".join(tree.xpath('//script[contains(text(), "var uluru")]/text()'))
                .split("lat:")[1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath('//script[contains(text(), "var uluru")]/text()'))
                .split("lng:")[1]
                .split("}")[0]
                .strip()
            )
            hours_of_operation = (
                "".join(tree.xpath('//div[@class="col col-md-5"]/p[2]/text()'))
                .replace("Office Hours:", "")
                .strip()
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
