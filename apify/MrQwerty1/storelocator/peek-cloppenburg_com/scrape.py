import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
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


def get_phone(page_url):
    r = session.get(page_url, headers=headers)
    logger.info(f"{page_url}: {r.status_code}")
    tree = html.fromstring(r.text)
    phone = "".join(tree.xpath("//p[contains(text(), 'Telefon')]/text()"))
    phone = phone.replace("Telefon", "").replace(":", "").strip()

    return phone


def get_api():
    r = session.get("https://www.peek-cloppenburg.com/en/stores/", headers=headers)
    tree = html.fromstring(r.text)
    key = "".join(
        tree.xpath("//script[contains(@src, '_buildManifest.js')]/@src")
    ).split("/")[-2]
    logger.info(f"Token is: {key}")

    return f"https://www.peek-cloppenburg.com/_next/data/{key}/en/stores.json"


def fetch_data(sgw: SgWriter):
    api = get_api()
    r = session.get(api, headers=headers)
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
            if "email" in text.lower() or "product" in text.lower():
                continue
            if "hours" in text.lower() or "Öffnungszeiten" in text:
                text = "Opening Hours"

            if text:
                line.append(text.strip())

        location_name = line.pop(0)
        index = line.index("Opening Hours")
        raw_address = " ".join(", ".join(line[:index]).split())
        street_address, city, postal = get_international(raw_address)

        _tmp = []
        text = line[index + 1 :]
        for t in text:
            if re.findall(r"\d{2}\.\d{2}\.\d{2}", t):
                continue
            _tmp.append(" ".join(t.split()))

        hours_of_operation = ";".join(_tmp)

        try:
            page_url = j["text"][-1]["spans"][-1]["data"]["url"]
            if phone == SgRecord.MISSING:
                try:
                    phone = get_phone(page_url)
                except Exception as e:
                    logger.info(f"Error during scraping phone: {e}")
        except:
            page_url = "https://www.peek-cloppenburg.com/en/stores/"

        country_code = SgRecord.MISSING
        if not page_url.endswith("/stores/"):
            country_code = page_url.split("cloppenburg.")[1].split("/")[0]

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            latitude=latitude,
            longitude=longitude,
            country_code=country_code,
            phone=phone,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
            store_number=store_number,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.peek-cloppenburg.com/"
    logger = sglog.SgLogSetup().get_logger(logger_name="peek-cloppenburg.com")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.STORE_NUMBER})
        )
    ) as writer:
        fetch_data(writer)
