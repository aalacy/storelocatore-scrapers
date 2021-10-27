from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import sglog

locator_domain = "https://jchristophers.com/"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)


def fetch_data(sgw: SgWriter):

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://jchristophers.com",
        "Connection": "keep-alive",
        "Referer": "https://jchristophers.com/locations/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    data = {"action": "get_all_stores", "lat": "", "lng": ""}

    r = session.post(
        "https://jchristophers.com/wp-admin/admin-ajax.php", headers=headers, data=data
    )
    js = r.json()
    for j in js.values():

        page_url = j.get("gu") or "<MISSING>"
        location_name = j.get("na") or "<MISSING>"
        street_address = j.get("st") or "<MISSING>"
        postal = j.get("zp") or "<MISSING>"
        country_code = "US"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = j.get("te") or "<MISSING>"
        city = location_name
        state = "<MISSING>"
        try:
            log.info(f"Page URL: {page_url}")
            r = SgRequests.raise_on_err(session.get(page_url, headers=headers))
            log.info(f"## Response: {r}")
        except Exception as e:
            log.info(f"Err at #L100: {e}")
            r = SgRequests.raise_on_err(
                session.get("https://jchristophers.com/locations/", headers=headers)
            )
            log.info(f"## Response: {r}")
        tree = html.fromstring(r.text)
        ad = (
            "".join(
                tree.xpath(
                    '//h3[text()="Visit Us"]/following-sibling::p[1]/a[2]/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if ad != "<MISSING>":
            city = ad.split(",")[0].strip()
            state = ad.split(",")[1].split()[0].strip()
        if city == "Canton":
            state = "Ohio"
        hours_of_operation = (
            "".join(tree.xpath('//p[contains(text(), "Serving Daily:")]/text()'))
            .replace("Serving", "")
            .strip()
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
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
