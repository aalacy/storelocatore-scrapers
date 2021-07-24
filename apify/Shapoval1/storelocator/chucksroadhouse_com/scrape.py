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
    locator_domain = "https://www.chucksroadhouse.com"
    page_url = "https://www.chucksroadhouse.com/locations/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./a[@class="cta-button "]]')

    for d in div:
        line = d.xpath(".//p[2]/text()")
        street_address = "".join(line[0])

        postal = "<MISSING>"
        state = "<MISSING>"
        country_code = "CA"
        store_number = "<MISSING>"
        location_name = "".join(d.xpath(".//h2/text()"))
        city = location_name
        phone = "".join(line[1])
        location_type = "<MISSING>"
        hours_of_operation = " ".join(line[-2:])

        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Referer": "https://cws.givex.com/cws5/chucksrhpwa/",
            "Content-Type": "text/plain;charset=UTF-8",
            "Origin": "https://cws.givex.com",
            "Connection": "keep-alive",
            "TE": "Trailers",
        }
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        data = '{"params":["en","1300","mqid","mqpass","TAKE_OUT"],"id":"1300"}'
        r = session.post(
            "https://cws.givex.com/cws40_svc/chucksrhpwa/consumer/info_vxl_1300.rpc",
            headers=headers,
            data=data,
        )
        js = r.json()["result"]["I2"]
        for j in js:
            strad = "".join(j.get("store_address"))
            stph = "".join(j.get("store_phone")).replace("+1 ", "").replace(" ", "-")
            if stph.count("-") != 2:
                stph = stph[:7] + "-" + stph[7:]
            if stph == phone:
                latitude = j.get("store_latitude")
                longitude = j.get("store_longitude")
                state = j.get("store_province")
                postal = j.get("store_postal")
                if latitude.find("-") != -1:
                    latitude = j.get("store_longitude")
                if longitude.find("-") == -1:
                    longitude = j.get("store_latitude")
            if strad == "41 Main Street" and strad == "6465 Millcreek Dr Unit110":
                state = j.get("store_province")
                postal = j.get("store_postal")

        if latitude == "None" or latitude == "0.0":
            latitude, longitude = "<MISSING>", "<MISSING>"

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
