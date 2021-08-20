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
    locator_domain = "https://www.williamsbrospharmacy.com"
    api_url = "https://www.williamsbrospharmacy.com/Locations.aspx"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers",
    }
    params = (("action", "generateJSON"),)
    cookies = {
        "__cfduid": "d81d5a41cc323d045da28091c712e069d1615653135",
        "cf_clearance": "bb8eed1fd2a4dee4c17df60909d4e79b656f1224-1615708779-0-250",
        "_ga": "GA1.2.511798551.1615653155",
        "_gid": "GA1.2.1699509386.1615653155",
        "cf_chl_prog": "a21",
        "ASP.NET_SessionId": "u353wh1gvfyg5goucc5kdl2e",
        "rl_visitor_history": "125c2ccb-5267-4baf-b59f-db0a1522ab54",
        "sifi_user_id": "undefined",
        "_gat_UA-55123242-29": "1",
    }
    r = session.get(api_url, headers=headers, cookies=cookies, params=params)
    js = r.json()

    for j in js:
        ad = j.get("Bubble")
        ad = html.fromstring(ad)
        div = "".join(ad.xpath('//div[@id="locationDiv"]/span/text()'))

        street_address = "".join(ad.xpath('//span[@class="address"]//text()'))
        city = div.split(",")[0].split()[0]
        postal = div.split(",")[1].strip()
        state = div.split(",")[0].split()[1]
        country_code = "US"
        location_name = j.get("Name")
        phone = "".join(
            ad.xpath('//b[contains(text(), "Phone")]/following-sibling::text()[1]')
        )
        latitude = j.get("Lat")
        longitude = j.get("Lng")
        if latitude == "0":
            latitude = "<MISSING>"
        if longitude == "0":
            longitude = "<MISSING>"
        location_type = (
            "".join(ad.xpath("//h2/following-sibling::span[1]/text()")) or "<MISSING>"
        )
        hours_of_operation = " ".join(
            ad.xpath('//h3[contains(text(), "Hours")]/following-sibling::p[1]/text()')
        )
        store_number = "<MISSING>"
        page_url = "https://www.williamsbrospharmacy.com/Locations"

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
