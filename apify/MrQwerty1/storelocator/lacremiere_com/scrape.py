from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def fetch_data(sgw: SgWriter):
    api = "https://lacremiere.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=en"
    r = session.get(api)
    tree = html.fromstring(r.text)
    items = tree.xpath("//item")

    for i in items:
        line = (
            "".join(i.xpath("./address/text()"))
            .replace("&#39;", "'")
            .replace("&#44;", ",")
            .replace("  ", " ")
        )
        adr = parse_address(International_Parser(), line)
        street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
            "None", ""
        ).strip()
        city = adr.city
        if city == "Chambly":
            street_address += " Périgny"
        state = adr.state
        postal = adr.postcode
        location_name = "".join(i.xpath("./location/text()"))
        store_number = "".join(i.xpath("./storeid/text()"))
        phone = "".join(i.xpath("./telephone/text()"))
        latitude = "".join(i.xpath("./latitude/text()"))
        longitude = "".join(i.xpath("./longitude/text()"))

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="CA",
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://lacremiere.com/"
    page_url = "https://lacremiere.com/trouvez-une-cremiere/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
