import csv
from lxml import etree
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

    locator_domain = "https://jugojuice.com/"
    api_url = "https://jugojuice.com/wp-content/plugins/superstorefinder-wp.old/ssf-wp-xml.php?wpml_lang=en&t=1623447578107"

    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)

    root = etree.fromstring(r.text)
    div = root.xpath("//locator/store/item")

    for d in div:

        page_url = (
            "".join(d.xpath(".//exturl/text()")) or "https://jugojuice.com/locations/"
        )
        ad = "".join(d.xpath(".//address/text()[1]"))
        street_address = ad.split("<br>")[0].replace("&#44;", ",").strip()
        city_state = ad.split("<br>")[1].strip()
        city = city_state.split(",")[0].strip()
        state = city_state.split(",")[1].strip()
        postal = ad.split("<br>")[2].strip()
        store_number = "<MISSING>"
        location_name = "".join(d.xpath(".//location/text()")).replace("&#39;", "`")
        latitude = "".join(d.xpath(".//latitude/text()"))
        longitude = "".join(d.xpath(".//longitude/text()"))
        country_code = "CA"
        location_type = "Jugo Juice"
        phone = "".join(d.xpath(".//telephone/text()"))
        hours_of_operation = (
            "".join(d.xpath(".//operatingHours//text()"))
            .replace("\n", "")
            .replace("<div>", "")
            .replace("</div>", "")
            .replace('<span style="white-space:pre">', "")
            .replace("</span>", "")
        )
        hours_of_operation = hours_of_operation.replace(
            '<span style="font-size: 12px;">', ""
        ).replace('<font color="#333333" face="Roboto, sans-serif">', "")
        hours_of_operation = (
            hours_of_operation.replace('<span style="font-size: 16px;">', "")
            .replace("</font>", "")
            .replace("&nbsp;", " ")
            .replace("&lt;br&gt;", "")
            .replace("<br>", "")
        )
        hours_of_operation = (
            hours_of_operation.replace("	​", " ")
            .replace("	", " ")
            .replace(
                '<span style="background-color: rgb(255, 255, 255); font-size: 16px;"><div style="">',
                "",
            )
        )
        hours_of_operation = (
            hours_of_operation.replace('<span style="white-space: pre;">', "")
            .replace('<div style="">', " ")
            .replace(
                '<p class="p1" style="margin-top: 0px; margin-bottom: 0px; font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; line-height: normal;">',
                "",
            )
        )
        hours_of_operation = (
            hours_of_operation.replace(
                '<span style="font-family: inherit; font-weight: inherit;">', ""
            )
            .replace("</p>", "")
            .replace('<font color="#000000" face="Helvetica Neue">', "")
        )
        if hours_of_operation.find("*") != -1:
            hours_of_operation = hours_of_operation.split("*")[0].strip()
        if hours_of_operation.find("(") != -1:
            hours_of_operation = hours_of_operation.split("(")[0].strip()
        hours_of_operation = hours_of_operation or "<MISSING>"
        if "Temporarily Closed" in location_name:
            location_type = "Temporarily Closed"

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
