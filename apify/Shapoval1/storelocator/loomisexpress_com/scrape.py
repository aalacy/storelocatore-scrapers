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

    locator_domain = "https://loomisexpress.com"
    api_url = "https://loomisexpress.com/loomship/Shipping/DropOffLocations"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[text()="Last"]')
    for d in div:
        last_page_url = int("".join(d.xpath(".//@href")).split("=")[1].strip())

        for i in range(1, last_page_url + 1):
            session = SgRequests()
            page_url = (
                f"https://loomisexpress.com/loomship/Shipping/DropOffLocations?page={i}"
            )
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            tr = tree.xpath('//tr[contains(@class, "gridrow")]')
            for t in tr:

                location_name = (
                    "".join(t.xpath(".//td[1]/text()")).replace("\n", "").strip()
                )
                street_address = "".join(t.xpath(".//td[2]/text()"))
                state = "".join(t.xpath(".//td[4]/text()"))
                postal = "".join(t.xpath(".//td[5]/text()"))
                country_code = "CA"
                city = "".join(t.xpath(".//td[3]/text()")).replace("\n", "").strip()
                store_number = "<MISSING>"
                phone = "".join(t.xpath(".//td[6]/text()[1]")).replace("\n", "").strip()
                if phone.find(",") != -1:
                    phone = phone.split(",")[0].strip()
                if phone.find("/") != -1:
                    phone = phone.split("/")[0].strip()
                if not phone.replace("-", "").isdigit():
                    phone = "<MISSING>"

                hours_of_operation = (
                    " ".join(t.xpath(".//td[6]/text()[position()>1]"))
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )
                if hours_of_operation.find("Located on") != -1:
                    hours_of_operation = hours_of_operation.split("Located on")[
                        0
                    ].strip()
                hours_of_operation = hours_of_operation.replace(
                    "Stat holidays (Canadian, B.C.) closed", ""
                ).strip()
                if hours_of_operation == "By appointment only":
                    hours_of_operation = "<MISSING>"
                longitude = "<MISSING>"
                latitude = "<MISSING>"
                location_type = "<MISSING>"
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
