import csv
import usaddress
from lxml import html
from concurrent import futures
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


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get("https://groundround.com/menu-location/", headers=headers)

    tree = html.fromstring(r.text)
    urls = tree.xpath("//div[@class='pm-staff-item-img-container']/a/@href")
    urls[1] = "https://mygroundround.com/specials/"
    urls[6] = "https://mygroundround.com/bar/"
    return urls


def get_data(url):
    locator_domain = "https://groundround.com"
    page_url = "".join(url)
    if page_url.find("https") == -1:
        page_url = f"https://groundround.com{url}"
    if page_url.find("/Gift-Cards") != -1:
        return
    if page_url.find("/Employment") != -1:
        return
    if page_url.find("http://www.grkitchenandtaps.com") != -1:
        return
    if page_url.find("neenah") != -1:
        page_url = "https://groundroundfoxcities.com/neenah/"
    if page_url.find("oshkosh") != -1:
        page_url = "https://groundroundfoxcities.com/oshkosh/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    location_name = "".join(
        tree.xpath(
            '//p[@class="pm-sub-header-title"]/span/text() | //p[@class="pm-sub-header-title"]/text()'
        )
    )
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//p[@class="pm-sub-header-message"]/text() | //p[contains(text(), "Bar")]/text()'
            )
        )
        .replace("Bar:", "")
        .replace("1130", "11:30")
        .strip()
    )
    if (
        hours_of_operation.find("closed") != -1
        or hours_of_operation.find("Closed") != -1
    ):
        hours_of_operation = "Temporarily closed"
    if hours_of_operation.find("Midnight") != -1:
        hours_of_operation = hours_of_operation.split("Midnight")[0].strip()
    if hours_of_operation.find("midnight") != -1:
        hours_of_operation = hours_of_operation.split("midnight")[0].strip()
    direct = "".join(tree.xpath("//a[contains(@href, 'Directions')]/@href"))
    if direct.find("https://groundround.com") == -1:
        direct = f"https://groundround.com{direct}"

    session = SgRequests()
    tag = {
        "Recipient": "recipient",
        "AddressNumber": "address1",
        "AddressNumberPrefix": "address1",
        "AddressNumberSuffix": "address1",
        "StreetName": "address1",
        "StreetNamePreDirectional": "address1",
        "StreetNamePreModifier": "address1",
        "StreetNamePreType": "address1",
        "StreetNamePostDirectional": "address1",
        "StreetNamePostModifier": "address1",
        "StreetNamePostType": "address1",
        "CornerOf": "address1",
        "IntersectionSeparator": "address1",
        "LandmarkName": "address1",
        "USPSBoxGroupID": "address1",
        "USPSBoxGroupType": "address1",
        "USPSBoxID": "address1",
        "USPSBoxType": "address1",
        "BuildingName": "address2",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }
    if location_name.find("Grand Forks") != -1:
        direct = "https://gfgroundround.com/directions"
    if location_name.find("Ponca City") != -1:
        direct = "https://groundround.com/contact-ponca-city"
    if location_name.find("Ponca City") != -1:
        direct = "https://groundround.com/Directions/211"
    if location_name.find("Grand Forks") != -1:
        direct = "https://groundround.com/Directions/7"
    subr = session.get(direct)
    subtree = html.fromstring(subr.text)

    line = (
        " ".join(
            subtree.xpath(
                '//h6[contains(text(), "Address")]/following-sibling::p[1]/text()'
            )
        )
        .replace("\n", "")
        .strip()
    )

    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = (
        f"{a.get('address1')} {a.get('address2')}".replace("None", "").strip()
        or "<MISSING>"
    )
    city = a.get("city") or "<MISSING>"
    postal = a.get("postal") or "<MISSING>"
    state = a.get("state") or "<MISSING>"
    if state.find("USA") != -1:
        state = state.split("USA")[0].strip()
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(
            subtree.xpath(
                '////h6[contains(text(), "Telephone")]/following-sibling::p[1]/text()'
            )
        )
        or "<MISSING>"
    )
    try:
        text = (
            "".join(
                subtree.xpath(
                    '//script[contains(text(), "var map = new google.maps.Map")]/text()'
                )
            )
            .split("var myLatLng = new google.maps.LatLng(")[1]
            .split(");")[0]
        )
    except IndexError:
        text = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    if location_name.find("Ponca City") != -1:
        latitude = text.split(",")[0]
        longitude = text.split(",")[1]
    if text != "<MISSING>":
        latitude = text.split(",")[0]
        longitude = text.split(",")[1]
    location_type = "<MISSING>"
    if page_url.find("https://groundroundfoxcities") != -1:
        ad = "".join(tree.xpath('//p[@class="footer-contact"]/a[1]/text()'))
        street_address = ad.split(",")[0].strip()
        city = ad.split(",")[1].strip()
        state = ad.split(",")[2].split()[0].strip()
        postal = ad.split(",")[2].split()[1].strip()
        phone = "".join(tree.xpath('//p[@class="footer-contact"]/a[2]/text()'))
        hours_of_operation = "<MISSING>"
        location_name = f"{city}, {state}"
    if page_url.find("neenah") != -1:
        session = SgRequests()
        r = session.get("https://groundroundfoxcities.com/neenah/hours/")
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="twelve"]/p//text()'))
            .replace("\n", "")
            .strip()
        )
    if page_url == "https://mygroundround.com/specials/":
        page_url = "https://mygroundround.com/locations/"
        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        location_name = "".join(
            tree.xpath(
                '//span[@id="MainContentArea_ContentModule11_CMSContentLabel"]/a[1]//text()'
            )
        )
        street_address = (
            "".join(
                tree.xpath(
                    '//span[@id="MainContentArea_ContentModule11_CMSContentLabel"]/a[1]/following-sibling::text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(
                tree.xpath(
                    '//span[@id="MainContentArea_ContentModule11_CMSContentLabel"]/a[1]/following-sibling::text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        city = ad.split(",")[0].strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        phone = (
            "".join(
                tree.xpath(
                    '//span[@id="MainContentArea_ContentModule11_CMSContentLabel"]/a[1]/following-sibling::a[1]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            "".join(
                tree.xpath(
                    '//span[@id="MainContentArea_ContentModule11_CMSContentLabel"]/a[1]/following-sibling::strong[1]/following-sibling::text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
            + " "
            + "".join(
                tree.xpath(
                    '//span[@id="MainContentArea_ContentModule11_CMSContentLabel"]/a[1]/following-sibling::strong[1]/following-sibling::text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            hours_of_operation.replace("(we serve food until 11pm)", "")
            .replace("(we serve food in the lounge until 12am)", "")
            .strip()
        )
        ll = "".join(
            tree.xpath(
                '//span[@id="MainContentArea_ContentModule11_CMSContentLabel"]/a[1]/@href'
            )
        )
        latitude = ll.split("@")[1].split(",")[0].strip()
        longitude = ll.split("@")[1].split(",")[1].strip()
    if page_url == "https://mygroundround.com/bar/":
        page_url = "https://mygroundround.com/locations/"
        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        location_name = "".join(
            tree.xpath(
                '//span[@id="MainContentArea_ContentModule11_CMSContentLabel"]/a[4]//text()'
            )
        )
        street_address = (
            "".join(
                tree.xpath(
                    '//span[@id="MainContentArea_ContentModule11_CMSContentLabel"]/a[4]/following-sibling::text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(
                tree.xpath(
                    '//span[@id="MainContentArea_ContentModule11_CMSContentLabel"]/a[4]/following-sibling::text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        city = ad.split(",")[0].strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        phone = (
            "".join(
                tree.xpath(
                    '//span[@id="MainContentArea_ContentModule11_CMSContentLabel"]/a[4]/following-sibling::a[1]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            "".join(
                tree.xpath(
                    '//span[@id="MainContentArea_ContentModule11_CMSContentLabel"]/a[4]/following-sibling::strong[1]/following-sibling::text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
            + " "
            + "".join(
                tree.xpath(
                    '//span[@id="MainContentArea_ContentModule11_CMSContentLabel"]/a[1]/following-sibling::strong[1]/following-sibling::text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            hours_of_operation.replace("(we serve food until 11pm)", "")
            .replace("(we serve food in the lounge until 12am)", "")
            .replace("(we serve food 11pm)", "")
            .strip()
        )
        ll = "".join(
            tree.xpath(
                '//span[@id="MainContentArea_ContentModule11_CMSContentLabel"]/a[4]/@href'
            )
        )
        latitude = ll.split("@")[1].split(",")[0].strip()
        longitude = ll.split("@")[1].split(",")[1].strip()

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
