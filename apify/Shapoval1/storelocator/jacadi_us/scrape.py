import csv
import json
from lxml import html
from sgrequests import SgRequests
from concurrent import futures


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


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Referer": "https://www.jacadi.us/store-finder?iframe=false+&q=%D0%9D%D1%8C%D1%8E-%D0%99%D0%BE%D1%80%D0%BA%2C+10001%2C+%D0%A1%D0%A8%D0%90&latitude=40.75368539999999&longitude=-73.9991637",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get("https://www.jacadi.us/store-finder", headers=headers)
    tree = html.fromstring(r.text)
    return tree.xpath("//li[@id='CA']/ul/li/a/@href | //li[@id='US']/ul/li/a/@href")


def get_data(url):
    locator_domain = "https://www.jacadi.us"
    page_url = f"https://www.jacadi.us{url}"
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    direct = " ".join(tree.xpath('//a[contains(text(), "Store")]/@href'))
    direct = f"https://www.jacadi.us{direct}"
    if direct.find("603/store/604") != -1:
        direct = "https://www.jacadi.us/store/603"
    if direct.find("384") != -1:
        direct = "https://www.jacadi.us/store/843"
    if direct.find("606 /store/604") != -1:
        direct = "https://www.jacadi.us/store/604"
    if direct.find("603 /store/604") != -1:
        direct = "https://www.jacadi.us/store/603"
    session = SgRequests()
    subr = session.get(direct)
    jsBlock = (
        "["
        + subr.text.split('<script type="application/ld+json">')[1].split("</script>")[
            0
        ]
        + "]"
    )
    js = json.loads(jsBlock)
    for j in js:
        page_url = direct
        slug = page_url.split("/")[-1].strip()
        page_url = f"https://www.jacadi.us/store/{slug}"
        a = j.get("address")
        street_address = "".join(a.get("streetAddress"))
        city = a.get("addressLocality")
        postal = a.get("postalCode")
        state = a.get("addressRegion") or "<MISSING>"
        country_code = a.get("addressCountry")
        store_number = slug
        location_name = j.get("name")
        phone = j.get("telephone")
        latitude = j.get("geo").get("latitude")
        longitude = j.get("geo").get("longitude")
        location_type = "<MISSING>"
        hours = j.get("openingHoursSpecification")
        tmp = []
        for h in hours:
            day = h.get("dayOfWeek")
            open = h.get("opens")
            close = h.get("closes")
            line = f"{day}:{open} - {close}"
            if open == "Closed":
                line = f"{day} - Closed"
            tmp.append(line)
        hours_of_operation = " | ".join(tmp) or "<MISSING>"

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
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
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
    scrape()
