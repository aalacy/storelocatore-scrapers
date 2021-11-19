import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address
from sglogging import sglog

locator_domain = "https://jysk.az/"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)


def fetch_data(sgw: SgWriter):

    api_url = "https://jysk.az/az/store.html"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    try:
        r = SgRequests.raise_on_err(session.get(api_url, headers=headers))
        log.info(f"## Response: {r}")
        tree = html.fromstring(r.text)
        js_block = "".join(tree.xpath('//div[@class="stores"]/@data-info'))
        js = json.loads(js_block)

        for j in js:
            page_url = "https://jysk.az/az/store.html"
            location_name = j.get("title")
            ad = j.get("address")
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "AZ"
            city = a.city or "<MISSING>"
            latitude = "".join(j.get("position")).split(",")[0].strip()
            longitude = "".join(j.get("position")).split(",")[1].strip()
            phone = j.get("phoneNumber")
            hours = j.get("workingHours")
            b = html.fromstring(hours)
            hours_of_operation = " ".join(b.xpath("//*//text()"))

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
                hours_of_operation=hours_of_operation,
                raw_address=ad,
            )

            sgw.write_row(row)
    except Exception as e:
        log.info(f"Err at #L100: {e}")


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.LATITUDE}))) as writer:
        fetch_data(writer)
