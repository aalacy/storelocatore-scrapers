from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.hebe.pl/sklepy"
    r = session.get(api)
    source = r.text.replace("</br>", "<br/>").replace("<br>", "<br/>")
    tree = html.fromstring(source)

    divs = tree.xpath(
        "//div[@class='storelist__item ui-expandable js-accordion-store js-store']"
    )
    for d in divs:
        location_name = "".join(d.xpath(".//h4/text()")).strip()
        street_address = location_name
        csz = "".join(
            d.xpath(".//p[contains(@class, 'storelist__subheader')]/text()")
        ).strip()
        city, postal = csz.split(", ")
        latitude = "".join(d.xpath("./@data-lat"))
        longitude = "".join(d.xpath("./@data-lng"))
        store_number = "".join(d.xpath("./@data-id"))
        page_url = f"https://www.hebe.pl/sklep?StoreID={store_number}"

        hours = d.xpath(
            ".//div[@class='store-hours']//text()|.//div[@class='storehours__content']//text()"
        )
        hours = list(filter(None, [h.strip() for h in hours]))
        if hours:
            hours_of_operation = ";".join(hours[1:])
        else:
            hours_of_operation = SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="PL",
            latitude=latitude,
            longitude=longitude,
            store_number=store_number,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.hebe.pl/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
