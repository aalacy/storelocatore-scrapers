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

    locator_domain = "https://joellas.com/"

    api_url = "https://joellas.com/locations.php"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath('//div[@class="locations-all"]')
    for b in block:
        slug = "".join(b.xpath(".//a[./img]/@href"))
        page_url = f"{locator_domain}{slug}"
        location_name = "".join(b.xpath(".//a/h3/text()")).replace(">", "").strip()
        location_type = "<MISSING>"
        adr = "".join(b.xpath(".//p[1]/text()[2]")).replace("\n", "").strip()
        street_address = "".join(b.xpath(".//p[1]/text()[1]"))
        if location_name.find("Clarksville") != -1:
            adr = "".join(b.xpath(".//p[1]/text()[3]")).replace("\n", "").strip()
            street_address = (
                "".join(b.xpath(".//p[1]/text()[1]"))
                + ""
                + "".join(b.xpath(".//p[1]/text()[2]"))
            )
        adr = adr.replace("Clarksville", "Clarksville,")
        country_code = "US"
        phone = "".join(b.xpath('.//a[contains(@href, "tel")]/text()'))
        state = adr.split(",")[1].split()[0].strip() or "<MISSING>"
        postal = adr.split(",")[1].split()[-1].strip() or "<MISSING>"
        city = adr.split(",")[0].strip() or "<MISSING>"
        store_number = "<MISSING>"
        hours_of_operation = (
            " ".join(b.xpath(".//p[2]//text()")).replace("\n", "").strip()
            + " "
            + "".join(b.xpath(".//p[3]//text()")).replace("\n", "").strip()
        )
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = (
            "".join(hours_of_operation)
            .replace("-", " - ")
            .replace("am", " am")
            .replace("pm", " pm ")
        )
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        ll = "".join(
            tree.xpath(
                '//div[@class="content-fullbleed paddingbottom-more"]/figure[1]/iframe/@src'
            )
        )

        latitude = ll.split("ll=")[1].split(",")[0]
        longitude = ll.split("ll=")[1].split(",")[1].split("&")[0]

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
