import csv
from lxml import html
import json
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

    locator_domain = "https://www.zippys.com"
    api_url = "https://www.googletagmanager.com/gtm.js?id=GTM-MFVKXDD"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    block = (
        "["
        + r.text.split('"vtp_input":["macro",10],')[1]
        .split('"vtp_map":["list",')[1]
        .split("]]")[0]
        + "]]"
    )
    block = eval(block)
    for b in block:
        phone = "".join(b[-1])
        page_url = "".join(b[2]).replace("\\", "")
        if page_url.find("https://www.fivestarseniorliving.com") == -1:
            page_url = "https://www.fivestarseniorliving.com" + page_url
        if (
            page_url.find(
                "https://www.fivestarseniorliving.com/wi/west-allis/meadowmere-mitchell-manor-west-allis"
            )
            != -1
        ):
            continue
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        jsblock = "".join(
            tree.xpath('//script[contains(text(), "addressLocality")]/text()')
        )
        try:
            js = json.loads(jsblock)
        except:
            continue
        for j in js["@graph"]:

            location_name = j.get("name")
            location_type = "<MISSING>"
            street_address = j.get("address").get("streetAddress")
            state = j.get("address").get("addressRegion")
            postal = j.get("address").get("postalCode")
            country_code = j.get("address").get("addressCountry")
            city = j.get("address").get("addressLocality")
            store_number = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
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
