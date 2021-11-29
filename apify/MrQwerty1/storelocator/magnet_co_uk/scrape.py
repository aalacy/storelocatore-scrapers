from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line, postal):
    adr = parse_address(International_Parser(), line, postcode=postal)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or SgRecord.MISSING
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def get_hours(page_url):
    _tmp = []
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    days = tree.xpath(
        "//h4[contains(text(), 'Opening hours')]/following-sibling::dl/dt/text()"
    )
    times = tree.xpath(
        "//h4[contains(text(), 'Opening hours')]/following-sibling::dl/dd//text()"
    )

    for d, t in zip(days, times):
        if t.find("(") != -1:
            t = t.split("(")[0]
        t = t.replace("*", "").replace("till", "-").strip()
        if t.lower().find("virt") != -1 or not t:
            t = "Closed"
        if t.lower().find("call") != -1 or t.lower().find("closed") != -1:
            t = "Closed"
        if t.lower().find("appointment") != -1 or t.lower().find("christmas") != -1:
            t = "Closed"

        _tmp.append(f"{d.strip()}: {t}")

    hoo = ";".join(_tmp) or "<MISSING>"

    if hoo.count("Closed") == 7:
        hoo = "Closed"

    return hoo


def fetch_data(sgw: SgWriter):
    r = session.get(
        "https://www.magnet.co.uk/stores/getcloseststores",
        headers=headers,
        params=params,
    )
    js = r.json()["stores"]

    for j in js:
        location_name = j.get("StoreName")
        slug = j.get("StoreUrl") or ""
        page_url = f"https://www.magnet.co.uk{slug}"

        line = j.get("Address") or ""
        line = line.strip()
        if line.endswith(","):
            line = line[:-1]
        if "Tel:" in line:
            line = line.split("Tel:")[0].strip()

        postal = line.split("\n")[-1].strip()
        if len(postal) > 8:
            postal = " ".join(line.split()[-2:])
        raw_address = line.replace("\r\n", " ").replace("\n", " ")
        street_address, city, state, postal = get_international(raw_address, postal)
        if city == SgRecord.MISSING and "Kitchen" in location_name:
            city = location_name.replace("Kitchen Showrooms ", "")

        store_number = j.get("PageId")
        phone = j.get("PhoneNumber")
        splits = ["Trade", "kitchen", "/"]
        for s in splits:
            if s in phone:
                phone = phone.split(s)[0].strip()

        phone = phone.lower()
        replaces = [".", ",", "showroom", "retail", "only", "(", ")", "-"]
        for rep in replaces:
            phone = phone.replace(rep, "").strip()

        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        hours_of_operation = get_hours(page_url)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="GB",
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.magnet.co.uk/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    params = (("limitedStoreTypes", ""),)
    with SgRequests() as session:
        with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
            fetch_data(writer)
