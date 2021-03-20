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
    locator_domain = "https://www.citybbq.com"
    api_url = "https://order.citybbq.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers",
    }

    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath('//ul[@id="ParticipatingStates"]/li')
    for i in block:
        url1 = "".join(i.xpath(".//a/@href"))
        url1 = f"https://order.citybbq.com{url1}"
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Referer": "https://order.citybbq.com/locations",
            "Upgrade-Insecure-Requests": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "TE": "Trailers",
        }
        cookies = {
            "_gcl_au": "1.1.1275666536.1616147724",
            "_ga": "GA1.2.1565131436.1616147732",
            "_gid": "GA1.2.169092942.1616147732",
            "_fbp": "fb.1.1616147732783.1672002159",
            "__cfduid": "d51d0f4f8d1b467178bce7dd202af32771616149617",
        }
        r = session.get(url1, headers=headers, cookies=cookies)
        trees = html.fromstring(r.text)
        block = trees.xpath("//h2")
        for n in block:
            page_url = "".join(n.xpath(".//a/@href"))
            session = SgRequests()
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                "Connection": "keep-alive",
                "Referer": "https://order.citybbq.com/locations",
                "Upgrade-Insecure-Requests": "1",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "Trailers",
            }
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            location_name = "".join(tree.xpath("//h1/text()")).replace("\n", "").strip()
            street_address = (
                "".join(tree.xpath('//span[@class="street-address"]/text()'))
                .replace("\n", "")
                .strip()
            )
            phone = (
                "".join(tree.xpath('//span[@class="tel"]/text()'))
                .replace("\n", "")
                .strip()
            )
            city = (
                "".join(tree.xpath('//span[@class="locality"]/text()'))
                .replace("\n", "")
                .strip()
            )
            state = (
                "".join(tree.xpath('//span[@class="region"]/text()'))
                .replace("\n", "")
                .strip()
            )
            country_code = "US"
            store_number = "<MISSING>"
            latitude = "".join(tree.xpath('//span[@class="latitude"]/span/@title'))
            longitude = "".join(tree.xpath('//span[@class="longitude"]/span/@title'))
            location_type = "<MISSING>"
            hours_of_operation = tree.xpath(
                '//dl[@id="available-business-hours-popover"]//text()'
            )
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = " ".join(hours_of_operation)
            postal = (
                "".join(tree.xpath('//span[@class="postal-code"]/text()'))
                .replace("\n", "")
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
