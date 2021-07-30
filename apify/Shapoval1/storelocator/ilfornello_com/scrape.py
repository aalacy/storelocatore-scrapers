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

    locator_domain = "https://ilfornello.com/"
    api_url = "https://ilfornello.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="wpb_column vc_column_container vc_col-sm-2"]//a')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        location_name = "".join(d.xpath(".//span/text()")).replace("\n", "").strip()

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        ad = tree.xpath('//a[contains(@href, "goo")]//text()')
        if location_name.find("BAYVIEW") != -1:
            ad = tree.xpath('//a[contains(@href, "goo")]/following::p[1]//text()')

        location_type = "<MISSING>"
        street_address = "".join(ad[0])
        city = "<MISSING>"
        if street_address.find(",") != -1:
            street_address = "".join(ad[0]).split(",")[0].strip()
            city = "".join(ad[0]).split(",")[1].strip()
        try:
            state = "".join(ad[0]).split(",")[2].split()[0].strip()
            postal = "".join(ad[0]).split(",")[2].split()[1:]
            postal = " ".join(postal)
        except:
            state = "<MISSING>"
            postal = "<MISSING>"
        country_code = "CA"

        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        phone = (
            " ".join(
                tree.xpath(
                    '//h3[text()="ORDER ONLINE"]/following-sibling::p//text() | //h3[./span[text()="ORDER ONLINE"]]/following-sibling::p//text() | //h3[contains(text(), "CONTACT US")]/following-sibling::p//text() | //h3[./span[contains(text(), "CONTACT US")]]/following-sibling::p//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if phone.find("order:") != -1:
            phone = phone.split("order:")[1].strip()
        if phone.find("[") != -1:
            phone = phone.split("[")[0].replace("/", "").strip()
        if phone.find("ORDER") != -1:
            phone = phone.split("ORDER")[0].strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//b[text()="HOURS OF OPERATION:"]/following-sibling::text() | //h3[./span[text()="HOURS"]]/following-sibling::p//text() | //strong[text()="Hours:"]/following-sibling::strong//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = " ".join(
                tree.xpath('//span[text()="HOURS"]/following::p[1]//text()')
            )
        if "closed until" in hours_of_operation:
            hours_of_operation = "Temporarily Closed"
        if hours_of_operation.find("*") != -1 and hours_of_operation.find("**") == -1:
            hours_of_operation = hours_of_operation.split("*")[0].strip()
        if hours_of_operation.find(".**") != -1:
            hours_of_operation = (
                hours_of_operation.split(".**")[1].split("*")[0].strip()
            )
        if hours_of_operation.find(").") != -1:
            hours_of_operation = (
                hours_of_operation.split(").")[1].split("Phone")[0].strip()
            )
        hours_of_operation = (
            hours_of_operation.replace("Our patio is now open", "")
            .replace("Hours:", "")
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
