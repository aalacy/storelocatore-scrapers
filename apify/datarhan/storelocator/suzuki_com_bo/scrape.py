from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.imcruz.com/rest/center.php?op=sucursales&marca=suzuki)"
    domain = "suzuki.com.bo"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        if poi["vnd_repuestos"] == "no":
            continue
        hoo = [
            e.replace("Repuestos: =", "")
            for e in poi["horario"].split("|")
            if "Repuestos" in e
        ]
        hoo_1_data = [e for e in hoo if "1,2,3,4,5=" in e][0]
        hoo_1 = f'LUN-VIE {hoo_1_data.replace("1,2,3,4,5=", "").replace("=", " a ").replace(":00:00", ":00").replace("0:00", "0")}'
        hoo_2_data = [e for e in hoo if "6=" in e][0]
        hoo_2 = f'SAB {hoo_2_data.replace("6=", "").replace("=", " a ").replace(":00:00", ":00").replace("0:00", "0")}'
        hoo = f"{hoo_1}, {hoo_2}"

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.suzuki.com.bo/sucursales/",
            location_name=poi["nombre"],
            street_address=poi["descripcion"],
            city=poi["depa"],
            state="",
            zip_postal="",
            country_code="BO",
            store_number=poi["id"],
            phone=poi["telf"].split("|")[0].split("int")[0].strip(),
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
