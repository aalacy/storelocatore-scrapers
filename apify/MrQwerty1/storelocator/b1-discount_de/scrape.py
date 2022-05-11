from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.b1-discount.de/index.php?option=com_storelocator&view=map&format=raw&searchall=1&Itemid=102&catid=-1&tagid=-1&featstate=0"
    r = session.get(api, headers=headers)
    source = r.text.replace("<![CDATA[", "").replace("]]>", "").encode()
    tree = html.fromstring(source)
    divs = tree.xpath("//marker")

    for d in divs:
        location_name = "".join(d.xpath("./name/text()")).strip()
        raw_address = "".join(d.xpath("./address/text()")).strip()
        street_address = raw_address.split(", ")[0]
        zc = raw_address.split(", ")[1]
        postal = zc.split()[0]
        city = zc.replace(postal, "").strip()
        country_code = "DE"
        store_number = "".join(d.xpath("./custom1/text()")).strip()
        phone = "".join(d.xpath("./phone/text()")).strip()
        latitude = "".join(d.xpath("./lat/text()")).strip()
        longitude = "".join(d.xpath("./lng/text()")).strip()
        hours_of_operation = (
            "".join(d.xpath("./custom4/text()")).replace(", ", ";").strip()
        )

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            raw_address=raw_address,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.b1-discount.de/"
    page_url = "https://www.b1-discount.de/maerkte"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
