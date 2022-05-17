from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sglogging import sglog

logger = sglog.SgLogSetup().get_logger(logger_name="publicstorage.com")


def get_urls():
    r = session.get("https://www.publicstorage.com/sitemap_plp.xml", headers=headers)
    tree = html.fromstring(r.content)

    return tree.xpath("//loc/text()")


def get_data(page_url, sgw: SgWriter):
    store_number = page_url.split("/")[-1]
    api_url = f"https://www.publicstorage.com/api/sitecore/properties/getpropertyjsonld?siteid={store_number}"
    r = session.get(api_url, headers=headers)
    logger.info(f"{api_url} >> Response: {r.status_code}")
    try:
        j = r.json()["@graph"][0]

        location_name = j.get("name")
        a = j.get("address")
        street_address = a.get("streetAddress")
        city = a.get("addressLocality")
        state = a.get("addressRegion")
        postal = a.get("postalCode")
        if len(postal) == 4:
            postal = f"0{postal}"
        country_code = a.get("addressCountry")
        phone = j.get("telephone") or ""
        phone = phone.replace("+", "")
        g = j.get("geo") or {}
        latitude = g.get("latitude")
        longitude = g.get("longitude")
        if str(latitude) == "0":
            return

        _tmp = []
        hours = j.get("openingHoursSpecification") or []
        for h in hours:
            day = ",".join(h.get("dayOfWeek"))
            start = h.get("opens")
            end = h.get("closes")
            _tmp.append(f"{day}: {start} - {end}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)

    except Exception as e:
        logger.info(
            f"Err 'Oops...Something went wrong':{e}, {api_url} >> Response: {r.status_code}"
        )
        pass


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    logger.info(f"Total Stores: {len(urls)}")
    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.publicstorage.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
