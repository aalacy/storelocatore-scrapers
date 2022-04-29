from lxml import html
from sgrequests import SgRequests
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api_url = "https://jugojuice.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=en&t=1628874552097"

    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)

    tree = html.fromstring(r.content)
    div = tree.xpath("//locator/store/item")

    for d in div:

        page_url = (
            "".join(d.xpath(".//exturl/text()")) or "https://jugojuice.com/locations/"
        )
        ad = "".join(d.xpath(".//address/text()[1]")).replace("&#44;", ",")
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        if street_address == "15":
            street_address = ad.split(",")[0].strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        city = a.city or "<MISSING>"
        location_name = (
            "".join(d.xpath(".//location/text()"))
            .replace("&#39;", "`")
            .replace(" â", "")
        )
        latitude = "".join(d.xpath(".//latitude/text()"))
        longitude = "".join(d.xpath(".//longitude/text()"))
        country_code = "CA"
        location_type = "Jugo Juice"
        phone = "".join(d.xpath(".//telephone/text()"))
        hours_of_operation = (
            "".join(d.xpath(".//exturl/following-sibling::*[1]/text()")) or "<MISSING>"
        )
        if hours_of_operation != "<MISSING>":
            a = html.fromstring(hours_of_operation)
            hours_of_operation = (
                " ".join(a.xpath("//*//text()"))
                .replace("â", "")
                .replace("ââ", "")
                .replace(" <br> ", " ")
                .replace("<br>", "")
                .replace("  ", " ")
                .replace(" 	 ", " ")
                .strip()
            )
        if hours_of_operation.find("*") != -1:
            hours_of_operation = hours_of_operation.split("*")[0].strip()
        if hours_of_operation.find("(") != -1:
            hours_of_operation = hours_of_operation.split("(")[0].strip()

        if "Temporarily Closed" in location_name:
            location_type = "Temporarily Closed"
        if "temporarily closed" in location_name:
            location_type = "Temporarily Closed"

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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://jugojuice.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
