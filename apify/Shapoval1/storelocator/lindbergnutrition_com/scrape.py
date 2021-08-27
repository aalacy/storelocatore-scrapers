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

    locator_domain = "https://lindbergnutrition.com"
    api_url = "https://lindbergnutrition.com/pages/hours-locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class, "site-footer__rte")]')
    a = 1
    for d in div:
        page_url = "https://lindbergnutrition.com/pages/hours-locations"
        location_name = "".join(d.xpath(".//p[1]//text()"))
        ad = "".join(d.xpath(".//p[3]//text()")).replace(
            "Manhattan Beach", "Manhattan_Beach"
        )
        location_type = "<MISSING>"
        street_address = " ".join(ad.split(",")[0].split()[:-1])
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "<MISSING>"
        city = ad.split(",")[0].split()[-1].replace("_", " ").strip()
        store_number = "<MISSING>"

        text = "".join(
            d.xpath(
                f'.//preceding::div[@class="grid grid--uniform grid--flush-bottom"]/div[{a}]//a/@href'
            )
        )
        a += 1
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = "".join(d.xpath(".//p[4]//text()"))
        hours_of_operation = (
            " ".join(d.xpath(".//p[2]//text()")).replace("\n", "").strip()
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
