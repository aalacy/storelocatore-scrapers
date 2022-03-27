from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
    }
    api = "https://www.craftbeermarket.ca/locations/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//article[@class='loop-item location']")

    for d in divs:
        location_name = "".join(d.xpath(".//h3/text()")).strip()
        page_url = "".join(d.xpath(".//a[./img]/@href"))
        line = "".join(d.xpath(".//h4/text()")).split(",")
        if len(line) == 1:
            line = d.xpath(".//i[@class='fal fa-clock']/following-sibling::text()")
            line = list(filter(None, [li.strip() for li in line])).pop()
            street_address, city = line.split(", ")
            state = SgRecord.MISSING
        else:
            state = line.pop().strip()
            city = line.pop().strip()
            street_address = ",".join(line).strip()

        phone = "".join(
            d.xpath(".//div[@class='location-contact-container']/a/text()")
        ).strip()
        o = tree.xpath(f"//option[text()='{location_name}']")[0]
        latitude = "".join(o.xpath("./@data-lat"))
        longitude = "".join(o.xpath("./@data-lng"))
        store_number = "".join(o.xpath("./@value"))
        if not store_number.isdigit():
            store_number = SgRecord.MISSING
        hours = d.xpath(".//div[@class='location-contact-container']/p/text()")
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours)
        if "April" in hours_of_operation:
            hours_of_operation = SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            country_code="CA",
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.craftbeermarket.ca/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
