import csv

from concurrent import futures
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


def get_params():
    r = session.get("https://www.ronjonsurfshop.com/location/default.aspx")
    tree = html.fromstring(r.text)
    view = "".join(tree.xpath("//input[@id='__VIEWSTATE']/@value"))
    val = "".join(tree.xpath("//input[@id='__EVENTVALIDATION']/@value"))

    return view, val


def get_urls():
    view, val = get_params()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "*/*",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "X-MicrosoftAjax": "Delta=true",
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "Origin": "https://www.ronjonsurfshop.com",
        "Connection": "keep-alive",
        "Referer": "https://www.ronjonsurfshop.com/location/default.aspx",
    }

    data = {
        "AjaxManager": "AjaxManager|btnSearch",
        "ctl03$txtSearch": "",
        "F_City": "",
        "F_State": "",
        "F_Zipcode": "",
        "drpDistance": "50",
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": view,
        "__VIEWSTATEGENERATOR": "173A34E9",
        "__EVENTVALIDATION": val,
        "__ASYNCPOST": "true",
        "btnSearch": "Search",
    }

    r = session.post(
        "https://www.ronjonsurfshop.com/location/default.aspx",
        headers=headers,
        data=data,
    )
    tree = html.fromstring(r.text)

    return tree.xpath("//a[contains(@href, 'detail.aspx?')]/@href")


def get_data(url):
    locator_domain = "https://www.ronjonsurfshop.com/"
    page_url = f"https://www.ronjonsurfshop.com/location/{url}"

    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//span[@id='lblLocationName']/text()")).strip()
    street_address = "".join(tree.xpath("//span[@id='lblAddress']/text()")).strip()
    csz = (
        "".join(tree.xpath("//span[@id='lblCityStateZip']/text()"))
        .replace(",", "")
        .split()
    )
    postal = csz.pop()
    state = csz.pop()
    city = " ".join(csz)
    country_code = "US"
    store_number = page_url.split("=")[-1]
    phone = "".join(tree.xpath("//span[@id='lblPhone']/text()")).strip()
    text = "".join(tree.xpath("//script[contains(text(), 'Gload')]/text()"))
    latitude = text.split("gLat =")[1].split(";")[0].strip()
    longitude = text.split("gLong =")[1].split(";")[0].strip()
    location_type = "<MISSING>"
    hours_of_operation = (
        "".join(tree.xpath("//span[@id='lblHours']/text()"))
        .replace(" and ", ";")
        .replace(".", "")
        .replace("Open", "")
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

    return row


def fetch_data():
    out = []
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=12) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    session = SgRequests()
    scrape()
