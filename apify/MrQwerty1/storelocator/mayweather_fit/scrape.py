from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sglogging import sglog


def get_hoo(url):
    r = session.get(url, headers=headers)
    logger.info(f"{url}: {r.status_code}")
    tree = html.fromstring(r.text)

    if tree.xpath("//span[contains(text(), 'COMING SOON')]"):
        return "COMING SOON"
    return SgRecord.MISSING


def fetch_data(sgw: SgWriter):
    api = "https://mayweather.fit/wp-admin/admin-ajax.php?action=asl_load_stores&lang=&load_all=1&layout=1"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        page_url = j.get("website")
        location_name = j.get("title")
        adr1 = j.get("street") or ""
        adr2 = j.get("street2") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("postal_code")
        country_code = "US"
        store_number = j.get("id")
        phone = j.get("phone") or ""
        phone = phone.replace("?", "")
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = get_hoo(page_url)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://mayweather.fit/"
    logger = sglog.SgLogSetup().get_logger(logger_name="mayweather.fit")
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
