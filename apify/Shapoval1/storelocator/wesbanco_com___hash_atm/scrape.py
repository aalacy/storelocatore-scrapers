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

    locator_domain = "https://www.wesbanco.com"
    api_url = "https://wesbanco.locatorsearch.com/GetItems.aspx"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }
    data = {
        "lat": "39.21709203409263",
        "lng": "-82.18770500000001",
        "searchby": "FCS|ATMDP|",
        "SearchKey": "",
        "rnd": "1624048678765",
    }

    r = session.get(api_url, headers=headers, data=data)
    tree = etree.fromstring(r.content)
    div = tree.xpath("//marker")

    for d in div:

        page_url = "https://www.wesbanco.com/locations/"
        location_name = "".join(d.xpath("./label//text()"))
        location_type = "<MISSING>"
        if "&" in location_name:
            location_type = "Branch & ATM"
        if "Branch" in location_name and "ATM" not in location_name:
            location_type = "Branch"
        if "Branch" not in location_name and "ATM" in location_name:
            location_type = "ATM"

        street_address = "".join(d.xpath(".//add1//text()"))
        ad = "".join(d.xpath(".//add2//text()"))
        if ad.find("<br>") != -1:
            ad = ad.split("<br>")[0].strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = (
            "".join(d.xpath(".//title//text()")).split("Loc=")[1].split('"')[0].strip()
        )
        latitude = "".join(d.xpath(".//@lat"))
        longitude = "".join(d.xpath(".//@lng"))
        try:
            phone = (
                "".join(d.xpath(".//add2//text()"))
                .split("<b>")[1]
                .split("</b>")[0]
                .strip()
            )
        except:
            phone = "<MISSING>"
        hours_of_operation = (
            " ".join(
                d.xpath('.//label[text()="Hours"]/following-sibling::contents//text()')
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if (
            hours_of_operation.find("Lobby:") != -1
            and hours_of_operation.find("Drive-thru:") != -1
        ):
            hours_of_operation = (
                hours_of_operation.split("Lobby:")[1]
                .split("Drive-thru:")[0]
                .replace("<br>", " ")
                .replace("</b>", "")
                .replace("<b>", "")
                .strip()
            )
        if hours_of_operation.find("Lobby:") != -1:
            hours_of_operation = (
                hours_of_operation.split("Lobby:")[1]
                .replace("<br>", " ")
                .replace("</b>", "")
                .replace("</div>", "")
                .strip()
            )
        if hours_of_operation.find("Drive-thru:") != -1:
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
