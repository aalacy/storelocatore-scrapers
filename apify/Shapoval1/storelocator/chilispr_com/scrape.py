from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://chilispr.com/"
    api_url = "https://chilispr.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=&t=1647618471213"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath("//locator/store/item")
    for d in div:

        page_url = "https://chilispr.com/restaurantes/"
        location_name = (
            "".join(d.xpath(".//location/text()"))
            .replace("MayagÃ¼ez", "Mayagüez")
            .replace("BayamÃ³n", "Bayamón")
            .strip()
        )
        ad = (
            "".join(d.xpath(".//address/text()"))
            .replace("&#44;", ",")
            .replace("&amp;", "&")
            .replace("MayagÃ¼ez", "Mayagüez")
            .replace("DÃ­az Way", "Díaz Way")
            .replace("BayamÃ³n", "Bayamón")
            .replace("OrtegÃ³n", "Ortegón")
            .replace("RÃ­o", "Río")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        if street_address == "506":
            street_address = "Plaza del Norte Mall 506"
        if street_address.find("725 West Main") != -1:
            street_address = street_address.replace("Pr", "").strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        postal = postal.replace("PR", "").strip()
        country_code = "PR"
        city = a.city or "<MISSING>"
        latitude = "".join(d.xpath(".//latitude/text()")) or "<MISSING>"
        longitude = "".join(d.xpath(".//longitude/text()")) or "<MISSING>"
        phone = (
            "".join(d.xpath(".//telephone/text()")).replace(
                "787-880-4884", "(787) 880-4884"
            )
            or "<MISSING>"
        )

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
            hours_of_operation=SgRecord.MISSING,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
