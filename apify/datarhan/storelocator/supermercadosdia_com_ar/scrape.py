from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://diaonline.supermercadosdia.com.ar/api/dataentities/FL/search?_fields=id,imagen,nombre,horarios,direccion,etiqueta,lat,long,tipo,extra_info&_where=(estado=true)"
    domain = "supermercadosdia.com.ar"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "application/vnd.vtex.ds.v10+json",
        "REST-Range": "resources=0-3000",
        "content-type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        location_name = poi["nombre"]
        street_address = poi["direccion"]
        latitude = poi["lat"]
        longitude = poi["long"]
        hoo = poi["horarios"]
        addr = parse_address_intl(location_name)
        city = addr.city

        item = SgRecord(
            locator_domain=domain,
            page_url="https://diaonline.supermercadosdia.com.ar/folletos",
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal="",
            country_code="AR",
            store_number=poi["id"],
            phone="",
            location_type=poi["tipo"],
            latitude=latitude,
            longitude=longitude,
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
