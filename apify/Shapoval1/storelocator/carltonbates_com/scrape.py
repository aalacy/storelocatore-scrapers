import csv
import time
from lxml import html
from sgselenium import SgFirefox


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

    locator_domain = "https://www.carltonbates.com"
    api_url = "https://carltonbates.com/resources/branch-locator"
    with SgFirefox() as fox:
        fox.get(api_url)
        time.sleep(10)
        a = fox.page_source
        tree = html.fromstring(a)
        div = tree.xpath('//span[./a[text()="Map Location"]]')

        for d in div:

            page_url = "https://www.carltonbates.com/content/branch-locator"
            location_name = "".join(d.xpath(".//preceding::strong[1]/text()"))
            ad = d.xpath(".//text()")
            ad = list(filter(None, [a.strip() for a in ad]))
            location_type = "<MISSING>"
            street_address = "".join(ad[0]).strip()
            adr = (
                "".join(ad[1])
                .replace("Charlotte NC 28269", "Charlotte, NC 28269")
                .strip()
            )
            state = adr.split(",")[1].split()[0].strip()
            postal = adr.split(",")[1].split()[1].strip()
            country_code = "US"
            city = adr.split(",")[0].strip()
            store_number = "<MISSING>"
            map_link = "".join(d.xpath(".//a/@href"))
            try:
                latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
                longitude = map_link.split("!4d")[1].strip().split("!")[0].strip()
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
            phone = "".join(ad[2])
            if phone.find("Phone:") == -1:
                phone = "<MISSING>"
            if phone.find("Phone:") != -1:
                phone = phone.replace("Phone:", "").strip()
            hours_of_operation = "<MISSING>"

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
