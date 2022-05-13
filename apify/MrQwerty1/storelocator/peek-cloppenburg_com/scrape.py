from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser
from sglogging import sglog


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, postal


def get_api():
    r = session.get("https://www.peek-cloppenburg.com/en/stores/", headers=headers)
    tree = html.fromstring(r.text)
    key = "".join(
        tree.xpath("//script[contains(@src, '_buildManifest.js')]/@src")
    ).split("/")[-2]
    logger.info(f"Token is: {key}")

    return f"https://www.peek-cloppenburg.com/_next/data/{key}/en/stores.json"


def get_urls():
    urls = []
    api = get_api()
    logger.info(f"The API URL: {api}")
    r = session.get(api, headers=headers)
    js = r.json()["pageProps"]["layoutDocs"]["countriesDoc"]
    for j in js:
        cc = j.get("country")
        if cc == "en":
            continue
        url = api.replace("/en/", f"/{cc}/")
        logger.info(f"Country {cc} was added")
        urls.append(url)

    return urls


def get_phone(page_url):
    r = session.get(page_url, headers=headers)
    logger.info(f"{page_url}: {r.status_code}")
    tree = html.fromstring(r.text)
    phone = "".join(tree.xpath("//p[contains(text(), 'Telefon')]/text()"))
    phone = phone.replace("Telefon", "").replace(":", "").strip()

    return phone


def get_data(api, sgw: SgWriter):
    r = session.get(api, headers=headers)
    if r.status_code != 200:
        return

    js = r.json()["pageProps"]["pageDoc"]["data"]["body"][1]["data"]["body"]
    logger.info(f"{api}: {r.status_code} | {len(js)} records found")

    for j in js:
        try:
            latitude = j["items"][1]["tab_map"]["latitude"]
            longitude = j["items"][1]["tab_map"]["longitude"]
        except:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
        j = j.get("primary") or {}

        store_number = j.get("store_id")
        line = []
        lines = j.get("text") or []

        phone = SgRecord.MISSING
        for li in lines:
            text = li.get("text")
            if "Telefon" in text:
                phone = (
                    text.replace("Telefon", "")
                    .replace(":", "")
                    .replace("as", "")
                    .strip()
                )
                if "Pro" in phone:
                    phone = " ".join(phone.split("Pro")[0].split())
                if "Dar" in phone:
                    phone = " ".join(phone.split("Dar")[0].split())
                continue
            if text:
                line.append(text)

        country = api.split("/")[-2]
        location_name = line.pop(0)
        raw_address = line.pop(0).replace("\n", ", ")
        street_address, city, postal = get_international(raw_address)
        try:
            page_url = j["text"][-1]["spans"][-1]["data"]["url"]
            if phone == SgRecord.MISSING:
                try:
                    phone = get_phone(page_url)
                except Exception as e:
                    logger.info(f"Error during scraping phone: {e}")
        except:
            page_url = f"https://www.peek-cloppenburg.com/{country}/stores/"

        hours_of_operation = SgRecord.MISSING
        if "Opening Hours" in line:
            _tmp = []
            hours = line[line.index("Opening Hours") + 1 :]
            for h in hours:
                if "Product" in h:
                    break
                _tmp.append(h)
            hours_of_operation = ";".join(_tmp).replace("\n", ";")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            latitude=latitude,
            longitude=longitude,
            country_code=country.upper(),
            phone=phone,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
            store_number=store_number,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    logger.info(f"{len(urls)} countries will be scraped")

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.peek-cloppenburg.com/"
    logger = sglog.SgLogSetup().get_logger(logger_name="peek-cloppenburg.com")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
