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

    locator_domain = "https://supremofoods.com"
    page_url = "https://supremofoods.com/locations.html"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./p[@class="Circular-Text-Head"]]')
    for d in div:
        location_name = (
            "".join(d.xpath('.//a[@class="nonblock"]/@href'))
            .split("place/")[1]
            .split("/")[0]
            .strip()
            .replace("+", " ")
            .replace("%26", "&")
            .replace("CitiGrocer", "Citi Grocer")
        )
        if location_name.find("323") != -1:
            location_name = "Supremo Food Market"

        location_type = "<MISSING>"
        street_address = "".join(d.xpath(".//p[1]/text()"))
        if street_address.find("117") != -1 or street_address.find("7500") != -1:
            street_address = street_address + " " + "".join(d.xpath(".//p[2]/text()"))
        ad = "".join(d.xpath(".//p[2]/text()"))
        if street_address.find("117") != -1 or street_address.find("7500") != -1:
            ad = "".join(d.xpath(".//p[3]/text()"))
        phone = "".join(d.xpath(".//p[3]/text()")).strip()
        if street_address.find("117") != -1 or street_address.find("7500") != -1:
            phone = "".join(d.xpath(".//p[4]//text()")).strip()
        phone = phone.replace("Tel:", "").replace("(Store)", "").strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[-1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        text = "".join(d.xpath('.//a[contains(text(), "Get")]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        if street_address.find("25 South Broad St.") != -1:
            latitude, longitude = "<MISSING>", "<MISSING>"
        hours_of_operation = "".join(d.xpath(".//p[6]//text()")).strip()
        if (
            street_address.find("117") != -1
            or street_address.find("7500") != -1
            or street_address.find("249") != -1
        ):
            hours_of_operation = "".join(d.xpath(".//p[7]//text()")).strip()

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
