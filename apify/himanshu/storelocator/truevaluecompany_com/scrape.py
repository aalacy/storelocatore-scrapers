from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://truevaluecompany.com"
base_url = "https://hosted.where2getit.com/truevalue/index_responsive.html"
json_url = "https://hosted.where2getit.com/truevalue/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E{}%3C%2Fappkey%3E%3Cgeoip%3E1%3C%2Fgeoip%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3E%3C%2Faddressline%3E%3Clongitude%3E%3C%2Flongitude%3E%3Clatitude%3E%3C%2Flatitude%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Csearchradius%3E5000%3C%2Fsearchradius%3E%3Cwhere%3E%3Cexcluded%3E%3Cdistinctfrom%3E1%3C%2Fdistinctfrom%3E%3C%2Fexcluded%3E%3Cor%3E%3Ctruevaluebranded%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ftruevaluebranded%3E%3Chg%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fhg%3E%3Cgr%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fgr%3E%3Cds%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fds%3E%3Cja%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fja%3E%3Ctaylorrental%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ftaylorrental%3E%3C%2For%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E"

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def get(_, key):
    if _.select_one(key):
        return _.select_one(key).text.strip()
    return ""


def fetch_data():
    with SgRequests() as session:
        app_key = (
            session.get(base_url, headers=_headers)
            .text.split("<appkey>")[1]
            .split("</appkey>")[0]
        )
        locations = bs(
            session.get(json_url.format(app_key), headers=_headers).text, "lxml"
        ).select("poi")
        for _ in locations:
            street_address = get(_, "address1")
            if get(_, "address2"):
                street_address += " " + get(_, "address2")
            hours = []
            for day in days:
                day = day.lower()
                open = get(_, f"{day}_open_time")
                close = get(_, f"{day}_close_time")
                if open:
                    hours.append(f"{day}: {open} {close}")

            location_type = ""
            if get(_, "carpetcleanerrental") == "1":
                location_type = "rental store"
            if get(_, "hg") == "1":
                location_type = "garden center"
            if get(_, "keycutting") == "1":
                location_type = "Hardware store"
            yield SgRecord(
                page_url=get(_, "tvurl")
                or "https://www.truevaluecompany.com/store-locator",
                store_number=get(_, "dealerid"),
                location_name=get(_, "name"),
                street_address=street_address,
                city=get(_, "city"),
                state=get(_, "state"),
                zip_postal=get(_, "postalcode"),
                country_code=get(_, "country"),
                phone=get(_, "phone"),
                latitude=get(_, "latitude"),
                longitude=get(_, "longitude"),
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
