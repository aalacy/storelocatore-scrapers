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


def get_data():
    rows = []
    locator_domain = "https://www.fieldandstreamshop.com/"
    api_url = "https://storelocator.fieldandstreamshop.com/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E8504915E-4CDF-11E5-9785-A69AF48ECC77%3C%2Fappkey%3E%3Cgeoip%3E1%3C%2Fgeoip%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddress1%3E%3C%2Faddress1%3E%3Ccity%3E%3C%2Fcity%3E%3Cstate%3E%3C%2Fstate%3E%3Cprovince%3E%3C%2Fprovince%3E%3Cpostalcode%3E%3C%2Fpostalcode%3E%3Caddressline%3E%3C%2Faddressline%3E%3Clongitude%3E%3C%2Flongitude%3E%3Clatitude%3E%3C%2Flatitude%3E%3Ccountry%3E%3C%2Fcountry%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Csearchradius%3E3000%3C%2Fsearchradius%3E%3Cstateonly%3E1%3C%2Fstateonly%3E%3Cwhere%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E"
    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.content)
    poi = tree.xpath("//poi")
    for p in poi:
        days = []
        tmp = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        addr1 = "".join(p.xpath(".//address1/text()")).capitalize()
        addr2 = "".join(p.xpath(".//address2/text()"))
        street_address = f"{addr1} {addr2}".strip()
        city = "".join(p.xpath(".//city/text()")).lower()
        state = "".join(p.xpath(".//state/text()"))
        postal = "".join(p.xpath(".//postalcode/text()"))
        country_code = "".join(p.xpath(".//country/text()"))
        store_number = "".join(p.xpath(".//clientkey/text()"))
        location_name = "".join(p.xpath(".//name/text()")).capitalize()
        phone = "".join(p.xpath(".//phone/text()"))
        page_url = f"https://stores.fieldandstreamshop.com/{state.lower()}/{city}/{store_number}/"
        latitude = "".join(p.xpath(".//latitude/text()"))
        longitude = "".join(p.xpath(".//longitude/text()"))
        location_type = "<MISSING>"
        for t in tmp:
            start = "".join(p.xpath(f".//{t}open/text()"))
            start = start[:2] + "." + start[2:]
            close = "".join(p.xpath(f".//{t}close/text()"))
            close = close[:2] + "." + close[2:]
            line = f"{t}: {start} - {close}"
            days.append(line)

        hours_of_operation = " | ".join(days)

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

        rows.append(row)
    return rows


def scrape():
    data = get_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
