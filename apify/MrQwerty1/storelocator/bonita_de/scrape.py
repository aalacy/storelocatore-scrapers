from lxml import html
from urllib.parse import unquote
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = f"https://www.bonita.de/de/de/shop_api/app/store_finder/search.json?address=&country=&distance=5000"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.json())
    divs = tree.xpath("//div[@class='card']")

    for d in divs:
        location_name = "".join(d.xpath(".//h3/text()")).strip()
        raw_address = unquote(
            "".join(d.xpath(".//a[contains(@href, 'search/')]/@href")).split("/")[-1]
        )
        adr = raw_address.split(", ")
        country_code = adr.pop()
        city = adr.pop()
        postal = adr.pop()
        street_address = ", ".join(adr)
        store_number = "".join(
            d.xpath(".//div[contains(@id, 'storeHeader-')]/@id")
        ).replace("storeHeader-", "")
        line = d.xpath(".//div[contains(@id, 'storeBody')]/div/text()")
        line = list(filter(None, [li.strip() for li in line]))
        phone = line.pop(0).replace("Tel.:", "").strip()
        hours_of_operation = ";".join(line)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            store_number=store_number,
            raw_address=raw_address,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.bonita.de/"
    page_url = "https://www.bonita.de/de/de/store_finder"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Alt-Used": "www.bonita.de",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
