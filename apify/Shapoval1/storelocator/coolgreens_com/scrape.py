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

    locator_domain = "https://coolgreens.com/"
    api_url = "https://coolgreens.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./div/a[contains(text(), "Explore")]]')

    for d in div:

        page_url = "".join(d.xpath('.//a[contains(text(), "Explore")]/@href'))
        if page_url.find("https://coolgreensfl.com") != -1:
            continue
        loc = " ".join(d.xpath(".//div[2]//text()")).replace("\n", "").strip()
        text = "".join(d.xpath('.//a[contains(@href, "/maps/")]/@href'))
        location_type = "restaurant"
        street_address = "".join(d.xpath(".//div[3]//a/text()[1]"))
        ad = (
            "".join(d.xpath(".//div[3]//a/text()[2]")).replace("\n", "").strip()
            or "<MISSING>"
        )
        state = "<MISSING>"
        postal = "<MISSING>"
        country_code = "US"
        city = "<MISSING>"
        if ad != "<MISSING>":
            city = ad.split(",")[0].strip()
            state = ad.split(",")[1].split()[0].strip()
            postal = ad.split(",")[1].split()[1].strip()
        store_number = "<MISSING>"
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = "".join(tree.xpath("//h2/text()")).replace("•", "").strip()
        if street_address == "Explore":
            street_address = "".join(tree.xpath("//h1/span[1]/text()"))
            ad = "".join(tree.xpath("//h1/span[2]/text()")) or "<MISSING>"
            if ad != "<MISSING>":
                city = ad.split(",")[0].strip()
                state = ad.split(",")[1].split()[0].strip()
                postal = ad.split(",")[1].split()[1].strip()
        fa = tree.xpath("//div[./div/h1]/following-sibling::div//p/span/text()")
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[./div/h1]/following-sibling::div//p/span[contains(text(), ":")]/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if loc.find("Temporarily") != -1:
            hours_of_operation = "Temporarily Closed"
        try:
            phone = "".join(fa[-1]).strip()
        except:
            phone = "<MISSING>"

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
