import csv
from lxml import html
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

    locator_domain = "https://www.acuonline.org/"
    api_url = "https://acuonline.locatorsearch.com/GetItems.aspx"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-type": "application/x-www-form-urlencoded",
        "Origin": "https://acuonline.locatorsearch.com",
        "Connection": "keep-alive",
        "Referer": "https://acuonline.locatorsearch.com/index.aspx",
    }

    data = {
        "lat": "33.749982679351234",
        "lng": "-84.39665",
        "searchby": "FCS|",
        "SearchKey": "",
        "rnd": "1623238994268",
    }

    r = session.get(api_url, headers=headers, data=data)
    tree = etree.fromstring(r.content)
    div = tree.xpath("//marker")
    for d in div:

        page_url = "https://www.acuonline.org/home/resources/locations"
        location_name = (
            "".join(
                d.xpath('.//label[text()="Address"]/following-sibling::title[1]/text()')
            )
            .replace("<br>", " ")
            .strip()
        )
        if location_name.find("Employees Only") != -1:
            continue
        location_type = "ACU Branches"

        street_address = "".join(d.xpath(".//add1/text()"))
        ad = "".join(d.xpath(".//add2/text()")).replace(",,", ",")
        if ad.find("<") != -1:
            ad = ad.split("<")[0].strip()
        phone = "".join(d.xpath(".//add2/text()")).split("<br>")[1:]
        phone = "".join(phone[-1]).replace("<b>", "").replace("</b>", "").strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        city = ad.split(",")[0].strip()
        country_code = "US"
        store_number = "<MISSING>"
        latitude = "".join(d.xpath(".//@lat"))
        longitude = "".join(d.xpath(".//@lng"))
        hours = "".join(d.xpath(".//contents//text()"))
        ho = html.fromstring(hours)
        hours_of_operation = " ".join(ho.xpath("//table//tr/td/text()")) or "<MISSING>"
        if hours_of_operation.count("Temporarily Closed") == 5:
            hours_of_operation = "Temporarily Closed"
        hours_of_operation = (
            hours_of_operation.replace("Lobby & Drive Thru:", "")
            .replace("Live Teller ITM:", "")
            .replace("| Live Teller ITM: 7:00 - 7:00", "")
            .replace("Lobby:", "")
            .replace("|  7:00 - 7:00", "")
            .replace(" | ITM Drive-Thru: 7:00 - 7:00", "")
            .replace(" |  9:00 - 1:00", "")
            .strip()
        )
        hours_of_operation = hours_of_operation.replace("	 ", " ")
        if hours_of_operation.find("| ITM Drive-Thru:") != -1:
            hours_of_operation = hours_of_operation.split("| ITM Drive-Thru:")[
                0
            ].strip()

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
