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

    locator_domain = "http://kevajuice.com/"
    api_url = "http://kevajuice.com/store-locator/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="tp-caption tp-fade"]/a')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        if page_url.find("nevada") != -1:
            continue

        if page_url.find("colorado") == -1:

            session = SgRequests()
            r = session.get(page_url, headers=headers)

            div = r.text.replace(
                "<td>Keva Juice #3 at Cottonwood", "<tr><td>Keva Juice #3 at Cottonwood"
            ).replace(
                "<td>Keva Juice #4 at Juan Tabo", "<tr><td>Keva Juice #4 at Juan Tabo"
            )
            tree = html.fromstring(div)
            div = tree.xpath("//table/tbody/tr | //table/tbody/td")
            for d in div:

                location_name = (
                    "".join(d.xpath("./td[1]/text()[1]")).strip() or "<MISSING>"
                )
                location_type = "<MISSING>"
                street_address = (
                    "".join(d.xpath(".//td[1]/text()[2]")).replace("\n", "").strip()
                    or "<MISSING>"
                )
                if street_address.find("Near Food") != -1:
                    street_address = (
                        street_address
                        + " "
                        + "".join(d.xpath(".//td[1]/text()[3]"))
                        .replace("\n", "")
                        .strip()
                    )
                if street_address == "<MISSING>":
                    street_address = (
                        "".join(d.xpath('.//a[contains(@href, "q=keva+juice")]/@href'))
                        or "<MISSING>"
                    )
                if street_address.find("700") != -1:
                    street_address = (
                        street_address.split("q=keva+juice")[1]
                        .split("Cop")[0]
                        .replace("+", " ")
                        .strip()
                    )
                if street_address.find("1929") != -1:
                    street_address = (
                        street_address.split("q=keva+juice")[1]
                        .split("Plano")[0]
                        .replace("+", " ")
                        .strip()
                    )

                phone = "".join(d.xpath(".//td[3]/text()")).strip() or "<MISSING>"
                ad = (
                    "".join(d.xpath(".//td[1]/text()[3]")).replace("\n", "").strip()
                    or "<MISSING>"
                )
                if ad.find("6600") != -1:
                    ad = (
                        "".join(d.xpath(".//td[1]/text()[4]")).replace("\n", "").strip()
                    )
                if (
                    street_address.find("700") != -1
                    or street_address.find("1929") != -1
                ):
                    ad = (
                        "".join(d.xpath('.//a[contains(@href, "q=keva+juice")]/@href'))
                        .split("Rd+")[1]
                        .split("&")[0]
                        .replace("+", " ")
                        .replace("Coppell", "Coppell,")
                        .replace("Plano", "Plano,")
                        .strip()
                    )
                state = "<MISSING>"
                postal = "<MISSING>"
                country_code = "US"
                city = "<MISSING>"
                if ad != "<MISSING>":
                    city = ad.split(",")[0].strip()
                    state = ad.split(",")[1].split()[0].strip()
                    postal = ad.split(",")[1].split()[-1].strip()
                store_number = "<MISSING>"
                text = "".join(d.xpath("./td[4]/a/@href")).strip()
                try:
                    if text.find("ll=") != -1:
                        latitude = text.split("ll=")[1].split(",")[0]
                        longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
                    else:
                        latitude = text.split("@")[1].split(",")[0]
                        longitude = text.split("@")[1].split(",")[1]
                except IndexError:
                    latitude, longitude = "<MISSING>", "<MISSING>"
                hours_of_operation = (
                    " ".join(d.xpath(".//td[2]/text()"))
                    .replace("\n", "")
                    .replace("Summer Hours", "")
                    .replace("Drive Thru Only:", "")
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

        if page_url.find("colorado") != -1:

            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            div = tree.xpath('//section[.//span[contains(text(), "Pickup")]]')
            for d in div:
                location_name = "".join(
                    d.xpath('.//span[@style="text-decoration:underline"]//text()')
                )
                location_type = "<MISSING>"
                street_address = "".join(
                    d.xpath('.//div/p[1]//span[@class="color_15"]/text()[1]')
                )
                phone = (
                    "".join(
                        d.xpath(
                            './/div/p[1]//span[@class="color_15"]/text()[2] | .//div/p[2]//span[@class="color_15"]/text()[1]'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                )
                state = "CO"
                postal = "<MISSING>"
                country_code = "US"
                city = "<MISSING>"
                store_number = "<MISSING>"
                hours_of_operation = (
                    " ".join(
                        d.xpath(
                            './/preceding::div[./h2//span[contains(text(), "Hours")]]/following-sibling::div[1]/p//text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                )
                latitude = "<MISSING>"
                longitude = "<MISSING>"

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
