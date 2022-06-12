from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from concurrent import futures


def get_urls():
    r = session.get(
        "https://www.renewalbyandersen.com/about/renewal-by-andersen-showrooms",
        headers=headers,
    )
    tree = html.fromstring(r.text)

    return set(tree.xpath("//a[contains(@href, 'window-company/')]/@href"))


def get_data(page_url, sgw: SgWriter):
    store_number = page_url.split("-")[1].split("/")[-1]
    if store_number.startswith("0"):
        store_number = store_number[1:]

    api = f"https://www.renewalbyandersen.com/api/sitecore/Maps/GetAffiliateShowrooms?ContextId=7A30CC0A254E4962BC80931A22EE5876&AffiliateId={store_number}"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        location_name = j.get("LocationName")
        adr1 = j.get("AddressLine1") or ""
        if "Mall" in adr1 or ":" in adr1:
            adr1 = ""
        adr2 = j.get("AddressLine2") or ""
        street_address = " ".join(f"{adr1} {adr2}".split())
        city = j.get("City")
        state = j.get("State")
        postal = j.get("Zip") or ""
        country_code = "US"
        if len(postal) > 5:
            country_code = "CA"
        phone = j.get("LocationPhoneNumber")
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        if str(latitude) == "0":
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        _tmp = []
        hours = j.get("Hours") or []
        for h in hours:
            day = h.get("Title")
            inter = h.get("Hours") or ""
            if not day or not inter or "n/a" in inter:
                continue

            inter = inter.lower()
            if "(" in inter:
                inter = inter.split("(")[0].strip()

            _tmp.append(f"{day}: {inter}")

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
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in get_urls()}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.renewalbyandersen.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
