import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():
    session = SgRequests()
    ur = []
    api_url = "https://api.merlins.com/api/stores/"
    r = session.get(api_url)
    js = json.loads(r.text)["message"]["stores"]
    for j in js:
        store_number = j.get("storeId")
        ur.append(store_number)
    return ur


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.merlins.com/"
    api_url = f"https://api.merlins.com/api/store/{url}"
    session = SgRequests()
    r = session.get(api_url)
    js = json.loads(r.text)["message"]
    for j in js:
        if not j:
            continue
        store_number = j.get("storeId")
        street_address = (
            f"{j.get('streetAddress1')} {j.get('streetAddress2')}" or "<MISSING>"
        ) or "<MISSING>"
        city = "".join(j.get("locationCity")) or "<MISSING>"
        state = "".join(j.get("locationState")) or "<MISSING>"
        postal = j.get("locationPostalCode") or "<MISSING>"
        country_code = "US"
        page_url = j.get("storeURL") or "<MISSING>"
        if page_url.find("plainfieldsouth") != -1:
            page_url = f"https://www.merlins.com/locations/{state.lower()}/{city.lower()}-{store_number}"
        if page_url.find("plainfieldnorth") != -1:
            page_url = f"https://www.merlins.com/locations/{state.lower()}/{city.lower()}-{store_number}"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        r = session.get(page_url)
        tree = html.fromstring(r.text)

        location_name = (
            " ".join(tree.xpath("//h1//text()")).replace("\n", "").strip()
            or "<MISSING>"
        )
        location_name = " ".join(location_name.split())
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[@class="location-content common-text"]/div[2]/p[position()>1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())

        row = SgRecord(
            locator_domain=locator_domain,
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
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
