from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.eroski.es/wp-admin/admin-ajax.php?action=store_search&lat=39.4699075&lng=-0.3762881&max_results=5000&radius=2000"
    domain = "eroski.es"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,ru-RU;q=0.8,ru;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": "https://www.eroski.es/tiendas/buscador-de-tiendas/",
        "Cookie": "TS01c86552=01301e525b86db460f8db1f6a8e2f44281b812ace3dc9377f725b05c242b642aa3c82b51f892cbd2c53bbf468146b30004b5b00fea; _gcl_au=1.1.614174468.1638352657; OptanonConsent=isIABGlobal=false&datestamp=Wed+Dec+01+2021+10%3A58%3A34+GMT%2B0100+(Central+European+Standard+Time)&version=6.12.0&hosts=&consentId=165701a5-b9b8-4c60-a6e0-1d6b6ad52910&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1%2CC0005%3A1%2CC0007%3A1&geolocation=ES%3BVC&AwaitingReconsent=false; OptanonAlertBoxClosed=2021-12-01T09:57:59.372Z; _ga=GA1.2.32920486.1638352680; _gid=GA1.2.609590439.1638352680; _dc_gtm_UA-111258381-1=1; _dc_gtm_UA-36762741-7=1; _fbp=fb.1.1638352681558.152205074; _hjSessionUser_534749=eyJpZCI6ImZlODIyMTFlLWRlMWYtNWIyNC1iNDRjLTg0MzM5YWQ4ZjgyZiIsImNyZWF0ZWQiOjE2MzgzNTI2ODE2NDcsImV4aXN0aW5nIjp0cnVlfQ==; _hjFirstSeen=1; _hjSession_534749=eyJpZCI6ImE4MWZmN2I1LWI0OTAtNDdjZC04MTEzLWFkOTdkYjg3ZDUxYiIsImNyZWF0ZWQiOjE2MzgzNTI2ODE2NzZ9; _hjAbsoluteSessionInProgress=0",
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        lun = f'Lunes: {poi["horario1"][0]}'
        mar = f'Mártes: {poi["horario2"][0]}'
        mie = f'Míercoles: {poi["horario3"][0]}'
        jue = f'Jueves: {poi["horario4"][0]}'
        vie = f'Viernes: {poi["horario5"][0]}'
        sab = f'Sabado: {poi["horario6"][0]}'
        dom = f'Domingo: {poi["horario7"][0]}'
        hoo = f"{lun}, {mar}, {mie}, {jue}, {vie}, {sab}, {dom}"

        item = SgRecord(
            locator_domain=domain,
            page_url=poi["permalink"],
            location_name=poi["store"],
            street_address=poi["address"],
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["zip"],
            country_code=poi["country"],
            store_number=poi["id"],
            phone=poi["phone"],
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
            hours_of_operation=hoo,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
