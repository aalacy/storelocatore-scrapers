from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = h.get("days")
        opens = h.get("hours").get("open")
        closes = h.get("hours").get("close")
        line = f"{day} {opens} - {closes}"
        tmp.append(line)
    return "; ".join(tmp)


def get_urls():

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(
        "https://www.costcutters.com/content/dam/sitemaps/costcutters/sitemap_costcutters_en_us.xml",
        headers=headers,
    )
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc[contains(text(), 'locations')]/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://costcutters.com/"
    page_url = "".join(url)
    if page_url.count("/") != 6:
        return

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)

    street_address = (
        "".join(
            tree.xpath(
                '//div[@class="maps-container"]/following-sibling::div[@class="salondetailspagelocationcomp"]//span[@itemprop="streetAddress"]/text()'
            )
        )
        or "<MISSING>"
    )
    city = (
        "".join(
            tree.xpath(
                '//div[@class="maps-container"]/following-sibling::div[@class="salondetailspagelocationcomp"]//span[@itemprop="addressLocality"]/text()'
            )
        )
        or "<MISSING>"
    )
    state = (
        "".join(
            tree.xpath(
                '//div[@class="maps-container"]/following-sibling::div[@class="salondetailspagelocationcomp"]//span[@itemprop="addressRegion"]/text()'
            )
        )
        or "<MISSING>"
    )
    postal = (
        "".join(
            tree.xpath(
                '//div[@class="maps-container"]/following-sibling::div[@class="salondetailspagelocationcomp"]//span[@itemprop="postalCode"]/text()'
            )
        )
        or "<MISSING>"
    )
    country_code = "US"
    location_name = (
        "".join(tree.xpath('//h2[@class="hidden-xs salontitle_salonlrgtxt"]/text()'))
        or "<MISSING>"
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
    store_number = (
        "".join(
            tree.xpath(
                '//script[contains(text(), "var salonIDSalonDetailPageLocationComp = ")]/text()'
            )
        )
        .split('var salonIDSalonDetailPageLocationComp = "')[1]
        .split('"')[0]
        .strip()
    )
    longitude = (
        "".join(
            tree.xpath(
                '//div[@class="maps-container"]/following-sibling::div[@class="salondetailspagelocationcomp"]//meta[@itemprop="longitude"]/@content'
            )
        )
        or "<MISSING>"
    )
    latitude = (
        "".join(
            tree.xpath(
                '//div[@class="maps-container"]/following-sibling::div[@class="salondetailspagelocationcomp"]//meta[@itemprop="latitude"]/@content'
            )
        )
        or "<MISSING>"
    )

    r = session.get(
        f"https://info3.regiscorp.com/salonservices/siteid/5/salon/{store_number}",
        headers=headers,
    )
    js = r.json()
    hours = js.get("store_hours") or "<MISSING>"
    hours_of_operation = "<MISSING>"
    if hours != "<MISSING>":
        hours_of_operation = get_hours(hours)

    if hours_of_operation == "M-F  - ; Sat  - ; Sun  -":
        hours_of_operation = "<MISSING>"
    if hours_of_operation.find("Mon  -") != -1:
        hours_of_operation = hours_of_operation.replace("Mon  -", "Mon  Closed")
    if hours_of_operation.find("Tue  -") != -1:
        hours_of_operation = hours_of_operation.replace("Tue  -", "Tue  Closed")
    if hours_of_operation.find("Wed  -") != -1:
        hours_of_operation = hours_of_operation.replace("Wed  -", "Wed  Closed")
    if hours_of_operation.find("Thu  -") != -1:
        hours_of_operation = hours_of_operation.replace("Thu  -", "Thu  Closed")
    if hours_of_operation.find("Fri  -") != -1:
        hours_of_operation = hours_of_operation.replace("Fri  -", "Fri  Closed")
    if hours_of_operation.find("Sat  -") != -1:
        hours_of_operation = hours_of_operation.replace("Sat  -", "Sat  Closed")
    if hours_of_operation.find("Sun  -") != -1:
        hours_of_operation = hours_of_operation.replace("Sun  -", "Sun  Closed")
    if hours_of_operation.find("M-F  - ;") != -1:
        hours_of_operation = "<MISSING>"
    if hours_of_operation.count("Closed") == 7:
        hours_of_operation = "<MISSING>"

    row = SgRecord(
        locator_domain=locator_domain,
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        location_type=SgRecord.MISSING,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
