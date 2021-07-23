import csv
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
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(
        "https://www.signaturestyle.com/content/dam/sitemaps/signaturestyle/sitemap_signaturestyle_en_us.xml",
        headers=headers,
    )
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc[contains(text(), 'locations')]/text()")


def get_data(url):
    locator_domain = "https://www.signaturestyle.com/"
    page_url = "".join(url)
    if page_url.count("/") != 6:
        return
    if (
        page_url
        == "https://www.signaturestyle.com/locations/on/brantford/first-choice-haircutters-51391.html"
    ):
        return
    if (
        page_url
        == "https://www.signaturestyle.com/locations/on/scarborough/first-choice-haircutters-51486.html"
    ):
        return
    if (
        page_url
        == "https://www.signaturestyle.com/locations/ns/sydney/first-choice-haircutters-51498.html"
    ):
        return
    if (
        page_url
        == "https://www.signaturestyle.com/locations/on/london/first-choice-haircutters-51372.html"
    ):
        return
    if (
        page_url
        == "https://www.signaturestyle.com/locations/on/london/first-choice-haircutters-51372.html"
    ):
        return
    if (
        page_url
        == "https://www.signaturestyle.com/locations/on/fergus/first-choice-haircutters-51511.html"
    ):
        return
    if (
        page_url
        == "https://www.signaturestyle.com/locations/on/tillsonburg/first-choice-haircutters-51471.html"
    ):
        return
    if (
        page_url
        == "https://www.signaturestyle.com/locations/on/milton/first-choice-haircutters-51507.html"
    ):
        return
    if (
        page_url
        == "https://www.signaturestyle.com/locations/on/petawawa/first-choice-haircutters-51496.html"
    ):
        return
    if (
        page_url
        == "https://www.signaturestyle.com/locations/on/london/first-choice-haircutters-51509.html"
    ):
        return
    if (
        page_url
        == "https://www.signaturestyle.com/locations/on/brantford/first-choice-haircutters-51390.html"
    ):
        return
    if (
        page_url
        == "https://www.signaturestyle.com/locations/on/london/first-choice-haircutters-51363.html"
    ):
        return
    if (
        page_url
        == "https://www.signaturestyle.com/locations/on/scarborough/first-choice-haircutters-51488.html"
    ):
        return
    if (
        page_url
        == "https://www.signaturestyle.com/locations/on/windsor/first-choice-haircutters-51397.html"
    ):
        return
    if (
        page_url
        == "https://www.signaturestyle.com/locations/on/ingersoll/first-choice-haircutters-51470.html"
    ):
        return
    if (
        page_url
        == "https://www.signaturestyle.com/locations/on/london/first-choice-haircutters-51369.html"
    ):
        return
    if (
        page_url
        == "https://www.signaturestyle.com/locations/ne/lincoln/cost-cutters-centennial-plaza-haircuts-16817.html"
    ):
        return
    if (
        page_url
        == "https://www.signaturestyle.com/locations/ns/sydney/first-choice-haircutters-51499.html"
    ):
        return
    if (
        page_url
        == "https://www.signaturestyle.com/locations/on/waterloo/first-choice-haircutters-51356.html"
    ):
        return
    if (
        page_url
        == "https://www.signaturestyle.com/locations/on/pembroke/first-choice-haircutters-51497.html"
    ):
        return
    if (
        page_url
        == "https://www.signaturestyle.com/locations/on/london/first-choice-haircutters-51514.html"
    ):
        return
    if (
        page_url
        == "https://www.signaturestyle.com/locations/on/london/first-choice-haircutters-51508.html"
    ):
        return
    if (
        page_url
        == "https://www.signaturestyle.com/locations/az/peoria/cost-cutters-agua-fria-haircuts-6920.html"
    ):
        return
    if (
        page_url
        == "https://www.signaturestyle.com/locations/al/alabaster/head-start-whitestone-center-haircuts-60204.html"
    ):
        return
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)

    street_address = (
        "".join(
            tree.xpath(
                '//div[@class="salon-address loc-details-edit"]//span[@itemprop="streetAddress"]/text()'
            )
        )
        .replace("\n", "")
        .strip()
        or "".join(
            tree.xpath(
                '//div[@class="maps-container"]/following-sibling::div[3]//span[@itemprop="streetAddress"]/text()'
            )
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    if street_address == "<MISSING>":
        street_address = (
            "".join(
                tree.xpath(
                    '//p[@itemprop="address"]//span[@itemprop="streetAddress"]//text()'
                )
            )
            or "<MISSING>"
        )
    city = (
        "".join(
            tree.xpath(
                '//div[@class="salon-address loc-details-edit"]//span[@itemprop="addressLocality"]/text()'
            )
        )
        .replace("\n", "")
        .strip()
        or "".join(
            tree.xpath(
                '//div[@class="maps-container"]/following-sibling::div[3]//span[@itemprop="addressLocality"]/text()'
            )
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    if city == "<MISSING>":
        city = (
            "".join(
                tree.xpath(
                    '//p[@itemprop="address"]//span[@itemprop="addressLocality"]//text()'
                )
            )
            or "<MISSING>"
        )
    state = (
        "".join(
            tree.xpath(
                '//div[@class="salon-address loc-details-edit"]//span[@itemprop="addressRegion"]/text()'
            )
        )
        .replace("\n", "")
        .strip()
        or "".join(
            tree.xpath(
                '//div[@class="maps-container"]/following-sibling::div[3]//span[@itemprop="addressRegion"]/text()'
            )
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    if state == "<MISSING>":
        state = (
            "".join(
                tree.xpath(
                    '//p[@itemprop="address"]//span[@itemprop="addressRegion"]//text()'
                )
            )
            or "<MISSING>"
        )
    postal = (
        "".join(
            tree.xpath(
                '//div[@class="salon-address loc-details-edit"]//span[@itemprop="postalCode"]/text()'
            )
        )
        .replace("\n", "")
        .strip()
        or "".join(
            tree.xpath(
                '//div[@class="maps-container"]/following-sibling::div[3]//span[@itemprop="postalCode"]/text()'
            )
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    if postal == "<MISSING>":
        postal = (
            "".join(
                tree.xpath(
                    '//p[@itemprop="address"]//span[@itemprop="postalCode"]//text()'
                )
            )
            or "<MISSING>"
        )
    country_code = "CA"
    if postal.isdigit():
        country_code = "US"
    store_number = page_url.split("-")[-1].split(".html")[0].strip()
    location_name = "".join(
        tree.xpath(
            '//div[@class="salon-address loc-details-edit"]//div[@class="h2 h3"]/text()'
        )
    ).replace("\n", "").strip() or "".join(
        tree.xpath('//h1[@class="hidden-xs salontitle_salonsmalltxt"]/text()')
    )
    phone = (
        "".join(
            tree.xpath(
                '//div[@class="salon-address loc-details-edit"]//span[@itemprop="telephone"]//text()'
            )
        )
        .replace("\n", "")
        .strip()
        or "".join(
            tree.xpath(
                '//div[@class="maps-container"]/following-sibling::div[3]//span[@itemprop="telephone"]//text()'
            )
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    if phone == "<MISSING>":
        phone = (
            "".join(
                tree.xpath(
                    '//p[@itemprop="address"]/following-sibling::span[1]//text()'
                )
            )
            or "<MISSING>"
        )
    try:
        latitude = (
            "".join(tree.xpath('//script[contains(text(), "salonDetailLat ")]/text()'))
            .split('salonDetailLat = "')[1]
            .split('"')[0]
        )
        longitude = (
            "".join(tree.xpath('//script[contains(text(), "salonDetailLat ")]/text()'))
            .split('salonDetailLng = "')[1]
            .split('"')[0]
        )
    except:
        latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "".join(
        tree.xpath(
            '//div[@class="salon-address loc-details-edit"]//small[@class="sub-brand"]/text()'
        )
    )
    if "hairmasters" in page_url:
        location_type = "Hairmasters"
    if "island-haircutting" in page_url:
        location_type = "Island Haircutting"
    if "first-choice" in page_url:
        location_type = "First Choice"
    if "cost-cutters" in page_url:
        location_type = "Cost Cutters"
    if "holiday-hair" in page_url:
        location_type = "Holiday Hair"
    if "famous-hair" in page_url:
        location_type = "Famous Hair"
    if "tgf-hair" in page_url:
        location_type = "TGF"
    if "city-looks" in page_url:
        location_type = "City Looks"
    if "saturdays" in page_url:
        location_type = "Saturdays"
    if "head-start" in page_url:
        location_type = "Head Start"
    if "style-america" in page_url:
        location_type = "Style America"

    hours_of_operation = tree.xpath(
        '//div[@class="salon-timings displayNone"]/span//text() | //div[@class="maps-container"]/following-sibling::div[3]//div[@class="store-hours sdp-store-hours"]/span//span//text() | //div[@class="store-hours sdp-store-hours"]/span/span/text()'
    )
    hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
    hours_of_operation = " ".join(hours_of_operation) or "<MISSING>"
    if hours_of_operation == "<MISSING>":
        jsurl = (
            f"https://info3.regiscorp.com/salonservices/siteid/5/salon/{store_number}"
        )
        session = SgRequests()
        r = session.get(jsurl, headers=headers)
        js = r.json()
        hooo = js.get("store_hours")
        tmp = []
        for h in hooo:
            day = h.get("days")
            opens = h.get("hours").get("open")
            closes = h.get("hours").get("close")
            line = f"{day} {opens}-{closes}"
            tmp.append(line)
            if opens == closes:
                line = f"{day} Closed"
                tmp.append(line)
        hours_of_operation = ";".join(tmp).replace("-;", "Closed;") or "<MISSING>"
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"
        if hours_of_operation.count("Closed") > 7:
            hours_of_operation = "Closed"
        if hours_of_operation.count("Closed") == 6:
            hours_of_operation = "Closed"
        if hours_of_operation == "Monday-Friday Closed Saturday Closed Sunday Closed":
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
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
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
