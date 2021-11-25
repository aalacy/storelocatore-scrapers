from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.toyota.co.th/index.php/app/dealer/fnc/json_dealer_list/page/1/keyword//province//district//type_of/1/type_sr/1/type_sc/1/type_bp/1/mode/more/lang/en"
    domain = "toyota.co.th"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    data = session.get(start_url, headers=hdr).json()
    for poi in data["data"]:
        if poi["showroom"] != "Y":
            continue
        raw_address = poi["en"]["address"]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2

        item = SgRecord(
            locator_domain=domain,
            page_url=poi["website"],
            location_name=poi["en"]["name"],
            street_address=street_address,
            city=addr.city,
            state=poi["en"]["province"],
            zip_postal=addr.postcode,
            country_code="TH",
            store_number=poi["branch_code"],
            phone=poi["tel_call_center"],
            location_type="",
            latitude=poi["location"]["lat"],
            longitude=poi["location"]["lon"],
            hours_of_operation=poi["en"]["showroom"]["open"],
            raw_address=raw_address,
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
