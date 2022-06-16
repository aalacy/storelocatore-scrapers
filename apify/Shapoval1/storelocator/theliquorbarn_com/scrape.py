from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.theliquorbarn.com"
    api_url = "https://www.theliquorbarn.com/pages/locations.html"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.theliquorbarn.com/account.php?action=account_details",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec- Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }
    cookies = {
        "SHOP_SESSION_TOKEN": "itlafldnh1ief0r1em2p1jggl9",
        "SHOP_SESSION_ROTATION_TOKEN": "2b8f917450c9aab09173da2530af07a314917359b3f4a32d21503bb5fe47269b",
    }
    r = session.get(api_url, headers=headers, cookies=cookies)
    tree = html.fromstring(r.text)
    div = tree.xpath('//tr[./td/p[@align="left"]]/td')

    for d in div:
        page_url = "https://www.theliquorbarn.com/pages/locations.html"
        ad = d.xpath(".//text()")
        ad = list(filter(None, [a.strip() for a in ad]))
        if "NOW OPEN!" in ad:
            ad.pop(0)
        location_name = "".join(ad[0]).replace(":", "").strip()
        adr = "".join(ad[2]).strip()
        street_address = adr.split(",")[0].strip()
        state = adr.split(",")[2].split()[0].strip()
        postal = adr.split(",")[2].split()[1].strip()
        country_code = "US"
        city = adr.split(",")[1].strip()
        map_link = "".join(d.xpath(".//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        phone = "".join(ad[5]).replace("Direct line:", "").strip()
        hours_of_operation = "".join(ad[4]).strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
