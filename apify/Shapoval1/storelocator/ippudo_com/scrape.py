import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get("https://stores.ippudo.com/sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath(
        "//url/loc[contains(text(), 'https://stores.ippudo.com/en/')]/text()"
    )


def get_data(url, sgw: SgWriter):
    locator_domain = "https://ippudo.com/"
    page_url = "".join(url)
    if page_url.count("/") != 4:
        return
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    store_number = page_url.split("/")[-1].strip()
    street_address = (
        " ".join(tree.xpath('//meta[@itemprop="streetAddress"]/@content'))
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    street_address = " ".join(street_address.split())
    if street_address == "<MISSING>":
        return
    city = (
        "".join(
            tree.xpath(
                '//div[@class="Core-address"]//span[@class="c-address-city"]//text()'
            )
        )
        or "<MISSING>"
    )
    state = (
        "".join(
            tree.xpath(
                '//div[@class="Core-address"]//span[@class="c-address-state"]//text()'
            )
        )
        or "<MISSING>"
    )
    postal = (
        "".join(
            tree.xpath(
                '//div[@class="Core-address"]//span[@class="c-address-postal-code"]//text()'
            )
        )
        or "<MISSING>"
    )
    country_code = (
        "".join(tree.xpath('//div[@class="Core-address"]//address/@data-country'))
        or "<MISSING>"
    )
    location_name = (
        "".join(tree.xpath("//h1//text()")).replace("\n", "").strip() or "<MISSING>"
    )
    phone = "".join(tree.xpath('//div[@itemprop="telephone"]//text()')) or "<MISSING>"
    hours = "".join(
        tree.xpath('//div[@class="c-hours-details-wrapper js-hours-table"]/@data-days')
    )
    latitude = (
        "".join(
            tree.xpath(
                '//div[@class="Core-address"]//meta[@itemprop="latitude"]/@content'
            )
        )
        or "<MISSING>"
    )
    longitude = (
        "".join(
            tree.xpath(
                '//div[@class="Core-address"]//meta[@itemprop="longitude"]/@content'
            )
        )
        or "<MISSING>"
    )
    tmp = []
    if hours:
        js = json.loads(hours)
        for j in js:
            day = j.get("day")
            try:
                opens = str(j.get("intervals")[0].get("start"))
                closes = str(j.get("intervals")[0].get("end"))
                if opens == "0":
                    opens = "000"
                if closes == "0":
                    closes = "000"
                if len(opens) == 3:
                    opens = f"0{opens}"

                if len(closes) == 3:
                    closes = f"0{closes}"
                line = f"{day}  {opens[:2]}:{opens[2:]} - {closes[:2]}:{closes[2:]}"
            except:
                line = f"{day} Closed"
            tmp.append(line)
    hours_of_operation = "; ".join(tmp) or "<MISSING>"

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
