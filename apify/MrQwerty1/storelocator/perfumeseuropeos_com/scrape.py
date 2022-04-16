from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from concurrent import futures


def get_ids():
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//select[@id='estados']/option[@value!='0']/@value")


def get_data(_id, sgw: SgWriter):
    data = {
        "estado": _id,
        "municipio": "0",
    }
    r = session.post(api, headers=headers, data=data)
    js = r.json()

    for j in js:
        location_name = j.get("nombre")
        source = j.get("calle_numero") or "<html>"
        tree = html.fromstring(source)
        street_address = " ".join(" ".join(tree.xpath("//text()")).split())
        city = j.get("nombre_asentamiento")
        state = j.get("nombre_estado")
        location_type = j.get("formato")
        country_code = "MX"
        latitude = j.get("latitud")
        longitude = j.get("longitud")

        hours = j.get("openingHours") or []
        hours_of_operation = ";".join(hours)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            country_code=country_code,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, _id, sgw): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.perfumeseuropeos.com/"
    page_url = "https://www.perfumeseuropeos.com/sucursales"
    api = "https://www.perfumeseuropeos.com//sucursales/resultados"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.perfumeseuropeos.com",
        "Connection": "keep-alive",
        "Referer": "https://www.perfumeseuropeos.com/sucursales",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
