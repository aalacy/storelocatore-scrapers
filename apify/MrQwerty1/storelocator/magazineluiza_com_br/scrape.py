import ssl
import time
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgselenium import SgChrome


def get_ids():
    ids = set()
    with SgChrome() as fox:
        fox.get("https://lojas.magazineluiza.com.br/buscar-filiais")
        time.sleep(3)
        source = fox.page_source

    tree = html.fromstring(source)
    states = tree.xpath("//select[@name='state']/option[@value!='']/@value")

    for state in states:
        req = session.get(
            f"https://lemon-sellers-api.magazineluiza.com.br/branches/groups?state={state}",
            headers=headers,
        )
        if req.status_code == 404:
            continue
        js = req.json()

        for j in js:
            neighborhoods = j.get("neighborhoods") or []

            for n in neighborhoods:
                branches = n.get("branches") or []

                for b in branches:
                    ids.add(b.get("id"))

    return ids


def get_data(store_number, sgw: SgWriter):
    api = f"https://lemon-sellers-api.magazineluiza.com.br/branches/{store_number}"
    page_url = f"https://lojas.magazineluiza.com.br/filiais/{store_number}/"
    r = session.get(api, headers=headers)
    if r.status_code != 200:
        return

    j = r.json()
    a = j.get("address") or {}
    adr1 = a.get("street") or ""
    adr2 = a.get("number") or ""
    street_address = f"{adr1} {adr2}".strip()
    city = a.get("city")
    state = a.get("state")
    postal = a.get("zipCode")
    country_code = "BR"
    name = a.get("neighborhood") or ""
    location_name = f"Loja {name}".strip()
    phone = j.get("phone")
    latitude = j.get("latitude")
    longitude = j.get("longitude")

    _tmp = []
    o = j.get("openingHours") or {}
    workdays = o.get("workingDays") or {}
    sat = o.get("saturday") or {}
    sun = o.get("sunday") or {}
    if workdays:
        start = workdays.get("opening")
        end = workdays.get("closing")
        _tmp.append(f"Mon-Fri: {start}-{end}")
    if sat:
        start = sat.get("opening")
        end = sat.get("closing")
        _tmp.append(f"Sat: {start}-{end}")
    if sun:
        start = sun.get("opening")
        end = sun.get("closing")
        _tmp.append(f"Sat: {start}-{end}")

    hours_of_operation = ";".join(_tmp)

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
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {executor.submit(get_data, _id, sgw): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.magazineluiza.com.br/"
    ssl._create_default_https_context = ssl._create_unverified_context
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Connection": "keep-alive",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
