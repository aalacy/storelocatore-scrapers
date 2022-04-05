from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "http://www.johnsonfitness.com.cn"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    data = {"Action": "StoreCoord", "province": "", "shopid": ""}

    r = session.post(
        "http://www.johnsonfitness.com.cn/Data/Purchasedpt.ashx",
        headers=headers,
        data=data,
    )
    js = r.json()
    for j in js:
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        data = {"Action": "MapRtnshop", "lng": f"{longitude}", "lat": f"{latitude}"}

        r = session.post(
            "http://www.johnsonfitness.com.cn/Data/Purchasedpt.ashx",
            headers=headers,
            data=data,
        )
        jss = r.json()
        for jj in jss:

            page_url = "http://www.johnsonfitness.com.cn/Purchasedpt/Offine"
            location_name = jj.get("name") or "<MISSING>"
            street_address = jj.get("address") or "<MISSING>"
            state = jj.get("state") or "<MISSING>"
            country_code = "CN"
            city = jj.get("city") or "<MISSING>"
            phone = j.get("Phone") or "<MISSING>"

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=SgRecord.MISSING,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=SgRecord.MISSING,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
