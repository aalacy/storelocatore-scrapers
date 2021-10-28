import httpx
import json
from lxml import html
from sgrequests import SgRequests
from sgpostal.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    with SgRequests() as http:

        locator_domain = "https://mcdonalds.co.id"
        api_url = "https://mcdonalds.co.id/location"

        r = http.get(url=api_url)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        js_block = (
            "".join(tree.xpath('//script[contains(text(), "var geojson")]/text()'))
            .split("var geojson = ")[1]
            .split("}}]}];")[0]
            + "}}]}]"
        )
        js = json.loads(js_block)
        for j in js[0]["features"]:
            page_url = "https://mcdonalds.co.id/location"
            location_name = j.get("properties").get("merchant")
            ad = "".join(j.get("properties").get("crossStreet"))
            a = parse_address(International_Parser(), ad)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            if street_address == "<MISSING>":
                street_address = "".join(j.get("properties").get("crossStreet"))
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = j.get("properties").get("country")
            city = a.city or "<MISSING>"
            store_number = j.get("properties").get("id")
            latitude = j.get("geometry").get("coordinates")[0]
            longitude = j.get("geometry").get("coordinates")[1]
            phone = j.get("properties").get("telephone")
            if city.isdigit():
                city = "<MISSING>"
            days = j.get("properties").get("days")
            hours = j.get("properties").get("hours")
            hours_of_operation = f"{days} {hours}"
            if hours == "always WIB":
                hours_of_operation = f"{days} {j.get('properties').get('opening')}"

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
