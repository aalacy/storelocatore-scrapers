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

    locator_domain = "https://www.pridestores.com"
    api_url = "https://www.pridestores.com/_api/wix-code-public-dispatcher/siteview/wix/data-web.jsw/find.ajax?gridAppId=3f7c87a7-aa4d-497a-b4a0-a2d817c3652e&instance=wixcode-pub.fe72f53d68984443e1013cf705aeaa52cdb39e8f.eyJpbnN0YW5jZUlkIjoiYTRkMTY0MzctN2FlOC00NjhlLWIyZjEtMjZjOWNhYTM2Yzg0IiwiaHRtbFNpdGVJZCI6IjAzNDgyY2Y0LWQxNTQtNDM4OC1hMDIzLTk0NGYzZjNlOGE3ZSIsInVpZCI6bnVsbCwicGVybWlzc2lvbnMiOm51bGwsImlzVGVtcGxhdGUiOmZhbHNlLCJzaWduRGF0ZSI6MTYxODg1NjExNzk5NywiYWlkIjoiMDJmMTUzYTgtMGY2ZS00Zjg1LWFkY2EtOWQ1Y2MzZGJjNDM5IiwiYXBwRGVmSWQiOiJDbG91ZFNpdGVFeHRlbnNpb24iLCJpc0FkbWluIjpmYWxzZSwibWV0YVNpdGVJZCI6ImJmNDc3NDBiLTMwMTAtNGY4Yy05YzI4LWY0NmE4MjYzNjNhYyIsImNhY2hlIjpudWxsLCJleHBpcmF0aW9uRGF0ZSI6bnVsbCwicHJlbWl1bUFzc2V0cyI6IlNob3dXaXhXaGlsZUxvYWRpbmcsSGFzRG9tYWluLEFkc0ZyZWUiLCJ0ZW5hbnQiOm51bGwsInNpdGVPd25lcklkIjoiMzY1ZTJhNjAtOGNlZS00ZDMwLWE0YTYtOWIyNTQ0NDRhYzNmIiwiaW5zdGFuY2VUeXBlIjoicHViIiwic2l0ZU1lbWJlcklkIjpudWxsfQ==&viewMode=site"
    session = SgRequests()
    querystring = {
        "gridAppId": "a5534314-58bf-4aee-aa37-7081ab10004e",
        "instance": "wixcode-pub.c080237ec7458a0cd208bcdf4cd9c3547b5db48c.eyJpbnN0YW5jZUlkIjoiYTRkMTY0MzctN2FlOC00NjhlLWIyZjEtMjZjOWNhYTM2Yzg0IiwiaHRtbFNpdGVJZCI6IjAzNDgyY2Y0LWQxNTQtNDM4OC1hMDIzLTk0NGYzZjNlOGE3ZSIsInVpZCI6bnVsbCwicGVybWlzc2lvbnMiOm51bGwsImlzVGVtcGxhdGUiOmZhbHNlLCJzaWduRGF0ZSI6MTYwMjU3Mzg5ODA4MywiYWlkIjoiMjRiNzA4NzktM2FmMi00MjJjLThkODktYjFkMmRlZGQ5NDNiIiwiYXBwRGVmSWQiOiJDbG91ZFNpdGVFeHRlbnNpb24iLCJpc0FkbWluIjpmYWxzZSwibWV0YVNpdGVJZCI6ImJmNDc3NDBiLTMwMTAtNGY4Yy05YzI4LWY0NmE4MjYzNjNhYyIsImNhY2hlIjpudWxsLCJleHBpcmF0aW9uRGF0ZSI6bnVsbCwicHJlbWl1bUFzc2V0cyI6IkFkc0ZyZWUsSGFzRG9tYWluLFNob3dXaXhXaGlsZUxvYWRpbmciLCJ0ZW5hbnQiOm51bGwsInNpdGVPd25lcklkIjoiMzY1ZTJhNjAtOGNlZS00ZDMwLWE0YTYtOWIyNTQ0NDRhYzNmIiwiaW5zdGFuY2VUeXBlIjoicHViIiwic2l0ZU1lbWJlcklkIjpudWxsfQ==",
        "viewMode": "site",
    }
    payload = '["Locations",null,[{"city":"asc"}],0,32,null,null]'
    API_headers = {
        "accept": "*/*",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
        "x-xsrf-token": "1602573509|I_OES7OmIT2s",
        "content-type": "application/json",
        "cache-control": "no-cache",
    }

    APICall = session.post(
        api_url, data=payload, headers=API_headers, params=querystring
    )
    js = APICall.json()
    for j in js["result"]["items"]:

        page_url = f"{locator_domain}{j.get('url')}".lower()
        location_type = "<MISSING>"
        street_address = "".join(j.get("address"))

        phone = j.get("phone")
        state = "<MISSING>"
        country_code = "US"
        city = "<MISSING>"
        ad = "".join(j.get("city"))
        if ad.find(",") != -1:
            city = ad.split(",")[0].strip()
            state = ad.split(",")[1].strip()
        store_number = "<MISSING>"
        hours_of_operation = (
            f"Mon-Fri:{j.get('hours')} Sat:{j.get('satHours')} Sun:{j.get('sunHours')}"
        )
        if hours_of_operation.count("hrs") == 3:
            hours_of_operation = j.get("hours")
        session = SgRequests()
        r = session.get(page_url, headers=API_headers)

        tree = html.fromstring(r.text)
        location_name = "".join(tree.xpath('//span[@style="font-size:47px"]//text()'))
        if location_name.find("(") != -1:
            location_name = location_name.split("(")[0].strip()
        if street_address.find("10 Jennings") != -1:
            location_name = "Pride Hartford Truck Stop I-91"
        ll = "".join(tree.xpath('//script[contains(text(), "streetAddress")]/text()'))
        try:
            postal = (
                ll.split(street_address)[1]
                .split("postalCode")[1]
                .split(":")[1]
                .replace("\\", "")
                .split(",n")[0]
                .replace('"', "")
                .replace(",", "")
                .strip()
            )
        except IndexError:
            postal = "<MISSING>"
        slug = street_address.replace(" ", "+").replace("N.", "N")
        if slug.find("234 East Main St") != -1:
            slug = "234 E Main St"
        try:
            map_link = ll.split(slug)[1].split("data=")[0]
            latitude = map_link.split("@")[1].split(",")[0]
            longitude = map_link.split("@")[1].split(",")[1]
        except IndexError:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
