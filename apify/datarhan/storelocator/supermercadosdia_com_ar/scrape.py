from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://diaonline.supermercadosdia.com.ar/api/dataentities/SW/search?_fields=drive,address,city,geo,hours,id,name,province,whitelabel&_where=active=true"
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

        item = SgRecord(
            locator_domain=domain,
            page_url="https://diaonline.supermercadosdia.com.ar/folletos",
            location_name=poi["name"],
            street_address=poi["address"],
            city=poi["city"],
            state=poi["province"],
            zip_postal="",
            country_code="AR",
            store_number=poi["whitelabel"],
            phone="",
            location_type="",
            latitude=poi["geo"].split(",")[0],
            longitude=poi["geo"].split(",")[-1],
            hours_of_operation=poi["hours"],
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
