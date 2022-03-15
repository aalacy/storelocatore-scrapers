from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address
from sglogging import sglog

locator_domain = "https://www.kfc.co.il"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)


def fetch_data(sgw: SgWriter):

    api_url = "https://www.kfc.co.il/branches/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    try:
        r = SgRequests.raise_on_err(session.get(api_url, headers=headers))
        tree = html.fromstring(r.text)
        div = "".join(tree.xpath("//div/@data-positions"))
        js = eval(div)
        for j in js:

            ad = "".join(j.get("address"))
            info = j.get("infowindow")
            a = html.fromstring(info)
            al = a.xpath("//*//text()")
            page_url = "https://www.kfc.co.il/kfc-branches/"
            location_name = "".join(al[1]).strip()
            aa = parse_address(International_Parser(), ad)
            street_address = f"{aa.street_address_1} {aa.street_address_2}".replace(
                "None", ""
            ).strip()
            postal = aa.postcode or "<MISSING>"
            country_code = "IL"
            city = aa.city or "<MISSING>"
            latitude = j.get("lat")
            longitude = j.get("lng")
            hours_of_operation = "".join(al[-1]).strip()
            r = session.get("https://www.kfc.co.il/branches/", headers=headers)
            tree = html.fromstring(r.text)
            phone = (
                "".join(
                    tree.xpath(
                        f'//h5[text()="{location_name}"]/following::div[./div/h2[text()="טלפון"]][1]/following-sibling::div[1]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            phone = " ".join(phone.split())

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=SgRecord.MISSING,
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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
