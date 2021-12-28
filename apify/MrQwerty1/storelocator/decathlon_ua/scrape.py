from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_coords_from_text(text):
    try:
        lat, lng = text.split("/@")[1].split(",")[:2]
    except IndexError:
        lat, lng = SgRecord.MISSING, SgRecord.MISSING

    return lat, lng


def fetch_data(sgw: SgWriter):
    api = "https://www.decathlon.ua/uk/c/28-contacts"
    r = session.get(api)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//div[@class='columns__item']")
    for d in divs:
        raw_address = "".join(d.xpath(".//a[@class='link-icon']/text()")).strip()
        if not raw_address:
            continue

        location_name = "".join(
            d.xpath(".//div[@class='column__title tt-u']/text()")
        ).strip()
        phone = "".join(
            d.xpath(
                ".//div[contains(text(), 'телефон')]/following-sibling::div[1]//text()"
            )
        ).strip()
        city = raw_address.split(", ")[0]
        if city == "Київ":
            street_address = " ".join(raw_address.split(", ")[1:])
        else:
            street_address = ", ".join(raw_address.split(", ")[-2:]).replace(".", "")

        text = "".join(d.xpath(".//a[@class='info__footer-link fw-bold']/@href"))
        latitude, longitude = get_coords_from_text(text)
        slug = "".join(d.xpath(".//a[contains(@class, 'yellow-btn')]/@href"))
        page_url = f"https://www.decathlon.ua{slug}"

        _tmp = []
        hours = d.xpath(".//div[@class='schedule__content']/ul/li")
        for h in hours:
            day = "".join(h.xpath("./span[1]/text()")).strip()
            inter = "".join(h.xpath("./span[2]/text()")).strip()
            _tmp.append(f"{day}: {inter}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            country_code="UA",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.decathlon.ua/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
