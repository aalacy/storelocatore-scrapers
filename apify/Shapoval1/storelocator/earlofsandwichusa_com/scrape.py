import csv
from sgscrape.sgpostal import International_Parser, parse_address
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
    allurls = []
    session = SgRequests()
    ca = session.get("https://locations.earlofsandwichusa.com/index.html")
    tree1 = html.fromstring(ca.text)
    li_ca = tree1.xpath(
        '//ul[@class="c-directory-list-content"]/li/a[contains(text(), "Canada")]/@href'
    )
    for i in range(len(li_ca)):
        allurls.append(li_ca[i])

    us1 = session.get("https://locations.earlofsandwichusa.com/us")
    tree2 = html.fromstring(us1.text)
    li_us1 = tree2.xpath(
        '//ul[@class="c-directory-list-content"]/li/a[contains(text(), "Georgia")]/@href'
    )
    for i in range(len(li_us1)):
        allurls.append(li_us1[i])

    us2 = session.get("https://locations.earlofsandwichusa.com/us/ca")
    tree3 = html.fromstring(us2.text)
    li_us2 = tree3.xpath(
        '//ul[@class="c-directory-list-content"]/li/span[contains(text(), "(1)")]/preceding-sibling::a[not(contains(text(), "Valley"))]/@href'
    )
    for i in range(len(li_us2)):
        allurls.append(li_us2[i])

    us3 = session.get("https://locations.earlofsandwichusa.com/us/fl")
    tree4 = html.fromstring(us3.text)
    li_us3 = tree4.xpath(
        '//ul[@class="c-directory-list-content"]/li[1]/span[contains(text(), "(1)")]/preceding-sibling::a/@href'
    )
    for i in range(len(li_us3)):
        allurls.append(li_us3[i])

    us4 = session.get("https://locations.earlofsandwichusa.com/us/nv/las-vegas")
    tree5 = html.fromstring(us4.text)
    li_us4 = tree5.xpath('//div[@class="Teaser-link Teaser-page"]/a/@href')
    for i in range(len(li_us4)):
        allurls.append(li_us4[i])

    us5 = session.get("https://locations.earlofsandwichusa.com/us/nc/cherokee")
    tree6 = html.fromstring(us5.text)
    li_us5 = tree6.xpath('//div[@class="Teaser-link Teaser-page"]/a/@href')
    for i in range(len(li_us5)):
        allurls.append(li_us5[i])

    us6 = session.get("https://locations.earlofsandwichusa.com/us/fl/tampa")
    tree7 = html.fromstring(us6.text)
    li_us6 = tree7.xpath('//div[@class="Teaser-link Teaser-page"]/a/@href')
    for i in range(len(li_us6)):
        allurls.append(li_us6[i])

    us7 = session.get("https://locations.earlofsandwichusa.com/us")
    tree8 = html.fromstring(us7.text)
    li_us7 = tree8.xpath(
        '//ul[@class="c-directory-list-content"]/li/a[contains(text(), "Idaho")]/@href'
    )
    for i in range(len(li_us7)):
        allurls.append(li_us7[i])

    us8 = session.get("https://locations.earlofsandwichusa.com/us/md/northeast")
    tree9 = html.fromstring(us8.text)
    li_us8 = tree9.xpath('//div[@class="Teaser-link Teaser-page"]/a/@href')
    for i in range(len(li_us8)):
        allurls.append(li_us8[i])

    us9 = session.get("https://locations.earlofsandwichusa.com/us")
    tree10 = html.fromstring(us9.text)
    li_us9 = tree10.xpath(
        '//ul[@class="c-directory-list-content"]/li/a[contains(text(), "Massachusetts")]/@href'
    )
    for i in range(len(li_us9)):
        allurls.append(li_us9[i])

    us10 = session.get("https://locations.earlofsandwichusa.com/us/nj/newark")
    tree11 = html.fromstring(us10.text)
    li_us10 = tree11.xpath('//div[@class="Teaser-link Teaser-page"]/a/@href')
    for i in range(len(li_us10)):
        allurls.append(li_us10[i])

    us11 = session.get("https://locations.earlofsandwichusa.com/us")
    tree12 = html.fromstring(us11.text)
    li_us11 = tree12.xpath(
        '//ul[@class="c-directory-list-content"]/li/a[contains(text(), "New York")]/@href'
    )
    for i in range(len(li_us11)):
        allurls.append(li_us11[i])

    us12 = session.get("https://locations.earlofsandwichusa.com/us/pa/philadelphia")
    tree13 = html.fromstring(us12.text)
    li_us12 = tree13.xpath('//div[@class="Teaser-link Teaser-page"]/a/@href')
    for i in range(len(li_us12)):
        allurls.append(li_us12[i])

    us13 = session.get("https://locations.earlofsandwichusa.com/us")
    tree14 = html.fromstring(us13.text)
    li_us13 = tree14.xpath(
        '//ul[@class="c-directory-list-content"]/li/a[contains(text(), "South Dakota")]/@href'
    )
    for i in range(len(li_us13)):
        allurls.append(li_us13[i])

    us14 = session.get("https://locations.earlofsandwichusa.com/us")
    tree15 = html.fromstring(us14.text)
    li_us14 = tree15.xpath(
        '//ul[@class="c-directory-list-content"]/li/a[contains(text(), "Texas")]/@href'
    )
    for i in range(len(li_us14)):
        allurls.append(li_us14[i])

    us15 = session.get("https://locations.earlofsandwichusa.com/us/ca/valley-center")
    tree16 = html.fromstring(us15.text)
    li_us15 = tree16.xpath('//div[@class="Teaser-link Teaser-page"]/a/@href')
    for i in range(len(li_us15)):
        allurls.append(li_us15[i])

    us17 = session.get("https://locations.earlofsandwichusa.com/us/fl")
    tree18 = html.fromstring(us17.text)
    li_us17 = tree18.xpath(
        '//ul[@class="c-directory-list-content"]/li[2]/span[contains(text(), "(1)")]/preceding-sibling::a/@href'
    )
    for i in range(len(li_us17)):
        allurls.append(li_us17[i])

    us18 = session.get("https://locations.earlofsandwichusa.com/us/fl/lake-worth")
    tree19 = html.fromstring(us18.text)
    li_us18 = tree19.xpath('//div[@class="Teaser-link Teaser-page"]/a/@href')
    for i in range(len(li_us18)):
        allurls.append(li_us18[i])

    us19 = session.get("https://locations.earlofsandwichusa.com/us/fl/miami")
    tree20 = html.fromstring(us19.text)
    li_us19 = tree20.xpath('//div[@class="Teaser-link Teaser-page"]/a/@href')
    for i in range(len(li_us19)):
        allurls.append(li_us19[i])

    us20 = session.get("https://locations.earlofsandwichusa.com/us/fl/okeechobee")
    tree21 = html.fromstring(us20.text)
    li_us20 = tree21.xpath('//div[@class="Teaser-link Teaser-page"]/a/@href')
    for i in range(len(li_us20)):
        allurls.append(li_us20[i])

    us21 = session.get("https://locations.earlofsandwichusa.com/us/fl/port-st--lucie")
    tree22 = html.fromstring(us21.text)
    li_us21 = tree22.xpath('//div[@class="Teaser-link Teaser-page"]/a/@href')
    for i in range(len(li_us21)):
        allurls.append(li_us21[i])

    us22 = session.get("https://locations.earlofsandwichusa.com/us/fl")
    tree23 = html.fromstring(us22.text)
    li_us22 = tree23.xpath(
        '//ul[@class="c-directory-list-content"]/li[7]/span[contains(text(), "(1)")]/preceding-sibling::a/@href'
    )
    for i in range(len(li_us22)):
        allurls.append(li_us22[i])

    us23 = session.get("https://locations.earlofsandwichusa.com/us/nc/murphy")
    tree24 = html.fromstring(us23.text)
    li_us23 = tree24.xpath('//div[@class="Teaser-link Teaser-page"]/a/@href')
    for i in range(len(li_us23)):
        allurls.append(li_us23[i])

    return allurls


def get_data(url):
    locator_domain = "https://earlofsandwichusa.com/"
    page_url = f"https://locations.earlofsandwichusa.com/{url}".replace(
        "../", ""
    ).replace("../../", "")
    if (
        page_url.find("cherokee") != -1
        or page_url.find("north-east") != -1
        or page_url.find("newark-liberty") != -1
        or page_url.find("philadelphia") != -1
        or page_url.find("777") != -1
        or page_url.find("florida-turnpike") != -1
        or page_url.find("miami/6984") != -1
        or page_url.find("okeechobee/florida") != -1
        or page_url.find("okeechobee/florida") != -1
    ):
        page_url = "".join(url)

    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://locations.earlofsandwichusa.com/us/fl/lake-worth",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    line = (
        " ".join(
            tree.xpath(
                "//h2[contains(text(), 'ADDRESS')]/following-sibling::p/text() | //div[@class='Nap-addressInner']//address/span//text()"
            )
        )
        .replace("\n", "")
        .strip()
    )
    a = parse_address(International_Parser(), line)

    location_name = "".join(
        tree.xpath(
            '//h1[@id="location-name"]//span[@class="LocationName-brand"]/text()'
        )
    ) or "".join(tree.xpath("//h1/span/text()"))
    street_address = f"{a.street_address_1} {a.street_address_2}".replace(
        "None", ""
    ).strip()
    city = a.city
    state = a.state
    postal = a.postcode
    country_code = "US"
    store_number = "<MISSING>"

    phone = "".join(
        tree.xpath(
            '//span[@id="telephone"]/text() | //h2[contains(text(), "PHONE")]/following-sibling::p/text()'
        )
    )
    ll = "".join(tree.xpath('//div[@id="map"]/iframe/@src | //noscript/img/@src'))
    if ll.find("center") != -1:
        ll = ll.split("center=")[1].split("&")[0].replace("%2C", ",")
    else:
        ll = ll.split("coord=")[1].split("&q")[0]

    latitude = ll.split(",")[0]
    longitude = ll.split(",")[1]
    location_type = "<MISSING>"

    day = tree.xpath('//table[@class="c-location-hours-details"]/tbody/tr/td[1]/text()')
    td = tree.xpath(
        '//div[@class="Nap-addressWrapper"]/following-sibling::div//span[@class="c-location-hours-details-row-intervals-instance "]'
    )
    _tmp = []
    tmp = []
    for t in td:
        open = "".join(t.xpath("./span[1]/text()"))
        close = "".join(t.xpath("./span[3]/text()"))
        line = f"{open} {close}"
        _tmp.append(line)
    if len(tmp) == 6:
        tmp.append("Closed")

    for d, t in zip(day, _tmp):
        tmp.append(f"{d.strip()}: {t.strip()}")
    hours2 = (
        " ".join(tree.xpath('//div[@id="store_hours"]/p//text()'))
        .replace("\n", "")
        .strip()
    )
    hours_of_operation = ";".join(tmp) or hours2 or "Closed"
    if hours_of_operation.count("Closed") == 7:
        hours_of_operation = "Closed"

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
