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

    locator_domain = "https://cashshop.ca/"

    api_url = "https://cashshop.ca/our-locations.asp"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)

    tree = html.fromstring(r.text)
    block = tree.xpath(
        '//option[text()="Select Location"]/following-sibling::option/@value'
    )
    for b in block:

        slug = "".join(b)
        session = SgRequests()
        data = {"location": slug, "useraction": "show", "id": ""}
        r = session.post(
            "https://cashshop.ca/our-locations.asp", headers=headers, data=data
        )
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="border-new"]')
        for d in div:

            page_url = "https://cashshop.ca/our-locations.asp"
            location_name = "<MISSING>"
            location_type = "Cash Shop"
            ad = d.xpath(".//strong[1]/following-sibling::text()")
            street_address = "".join(ad[1]).replace("\r\n", "").strip()

            adr = "".join(ad[2]).replace("\r\n", "").strip()
            if street_address.find("3201") != -1:
                adr = " ".join(street_address.split(",")[1:])
                street_address = street_address.split(",")[0]
            street_address = street_address.replace(",", "")
            adr = adr.replace("ON,", "").replace("North York", "North York,")
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            country_code = "CA"
            state = "<MISSING>"
            postal = adr.split(",")[1].strip()
            city = adr.split(",")[0].strip()
            store_number = "<MISSING>"
            hours_of_operation = d.xpath(
                './/strong[text()=" Store hours"]/following::text()'
            )
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = " ".join(hours_of_operation).split("Ph")[0].strip()
            phone = (
                "".join(
                    d.xpath('.//strong[text()=" Ph No"]/following-sibling::text()[1]')
                )
                .split("Ext")[0]
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
