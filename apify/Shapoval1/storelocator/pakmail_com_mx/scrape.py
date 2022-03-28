import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures
from sglogging import sglog

locator_domain = "pakmail.com.mx"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)


def get_urls():

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(
        "https://engine.aceleradordigitaldenegocios.com.mx/sucursalesPakmail",
        headers=headers,
    )
    js = r.json()
    urls = []
    for j in js:
        slug = "".join(j.get("sitio"))
        if slug.find("plaza-samara-.pakmail.com.mx") != -1:
            slug = "plaza-samara.pakmail.com.mx"
        page_url = f"https://{slug}"
        urls.append(page_url)
    return urls


def get_data(url, sgw: SgWriter):

    page_url = url
    log.info(f"Page URL: {page_url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "TE": "trailers",
    }
    try:
        result = SgRequests.raise_on_err(session.get(page_url, headers=headers))
        log.info(f"## Response: {result}")
        tree = html.fromstring(result.text)

        jsBlock = (
            "".join(tree.xpath('//script[@type="application/ld+json"]/text()'))
            .replace("//<![CDATA[", "")
            .replace("//]]>", "")
            .strip()
        )
        js = json.loads(jsBlock)
        a = js.get("address")
        street_address = a.get("streetAddress") or "<MISSING>"
        city = "".join(a.get("addressLocality")) or "<MISSING>"
        if city.find(",") != -1:
            city = city.split(",")[0].strip()
        state = a.get("addressRegion") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = "MX"
        location_name = js.get("name") or "<MISSING>"
        phone = js.get("telephone") or "<MISSING>"
        hours = js.get("openingHours")
        try:
            hours_s = eval(hours)
        except:
            hours_s = "<MISSING>"
        hours_of_operation = "<MISSING>"
        if hours_s != "<MISSING>":
            hours_of_operation = " ".join(hours_s)

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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)

    except Exception as e:
        log.info(f"Err at #L100: {e}")


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
