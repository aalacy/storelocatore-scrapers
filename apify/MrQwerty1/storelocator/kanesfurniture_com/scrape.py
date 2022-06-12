from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    page_url = "https://www.kanesfurniture.com/pages/store-locations"

    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//article[@class='location']")

    for d in divs:
        location_name = "".join(d.xpath(".//h4[@class='location__hdg']/text()")).strip()
        line = d.xpath(".//address[@class='location__address']/p/text()")
        line = list(filter(None, [l.strip() for l in line]))

        street_address = line[0]
        line = line[1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"

        phone = (
            "".join(d.xpath(".//a[@class='location__phone']/text()")).strip()
            or "<MISSING>"
        )
        latitude = "".join(d.xpath("./@data-lat")) or "<MISSING>"
        longitude = "".join(d.xpath("./@data-lng")) or "<MISSING>"

        _tmp = []
        keys = d.xpath(".//div[@class='location__hours']/p/strong/text()")
        values = d.xpath(".//div[@class='location__hours']/p/text()")
        values = list(filter(None, [v.strip() for v in values]))

        for k, v in zip(keys, values):
            _tmp.append(f"{k.strip()} {v.strip()}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        row = SgRecord(
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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.kanesfurniture.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
