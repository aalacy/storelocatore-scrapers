from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    page_url = "https://www.serenaandlily.com/stores.html"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    divs = tree.xpath(
        "//div[contains(@class, '-region col-sm-6') and .//*[text()='BOOK US']]"
    )
    for d in divs:
        line = d.xpath(".//text()")
        line = list(filter(None, [l.strip() for l in line]))
        line.pop(0)

        cnt = 0
        for li in line:
            if "@" in li:
                break
            cnt += 1

        line = line[:cnt]
        location_name = line.pop(0)
        if "opening" in location_name.lower():
            continue
        phone = line.pop()
        csz = line.pop().split(", ")
        city = csz.pop(0)
        state, postal = csz.pop().split()
        street_address = ", ".join(line)
        if location_name in street_address:
            street_address = street_address.replace(f"{location_name}, ", "")
        if ", AT" in street_address:
            street_address = street_address.split(", AT")[0]

        text = "".join(d.xpath(".//a[contains(@href, 'google')]/@href"))
        try:
            latitude, longitude = text.split("/@")[1].split(",")[:2]
        except IndexError:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.serenaandlily.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.serenaandlily.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "max-age=0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
