from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_phones(page_url):
    phones = []
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//h4[contains(text(), 'Stores')]/following-sibling::ul/li")

    for d in divs:
        phone = "".join(
            d.xpath(".//span[contains(text(), 'Telephone')]/following-sibling::text()")
        )
        if phone.istitle():
            phone = SgRecord.MISSING
        phones.append(phone)

    return phones


def get_data(_zip, sgw: SgWriter):
    api = f"http://www.maceni.co.uk/stores/markers/{_zip}/2000/"
    page_url = f"http://www.maceni.co.uk/stores/results/{_zip}/2000/"
    r = session.get(api, headers=headers)
    if r.status_code != 200:
        return

    tree = html.fromstring(r.content)
    divs = tree.xpath("//marker")
    phones = get_phones(page_url)

    for d, phone in zip(divs, phones):
        street_address = "".join(d.xpath("./@address1"))
        city = "".join(d.xpath("./@city"))
        postal = "".join(d.xpath("./@postcode"))
        country_code = "GB"
        location_name = "".join(d.xpath("./@name"))
        latitude = "".join(d.xpath("./@lat"))
        longitude = "".join(d.xpath("./@lng"))

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    zips = [f"BT{i}" for i in range(1, 101)]

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, _zip, sgw): _zip for _zip in zips}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "http://www.maceni.co.uk/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
