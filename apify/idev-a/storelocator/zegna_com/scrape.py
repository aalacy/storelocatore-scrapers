from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

hours_object = {
    "1": "Monday",
    "2": "Tuesday",
    "3": "Wednesday",
    "4": "Thursday",
    "5": "Friday",
    "6": "Saturday",
    "7": "Sunday",
}


def fetch_data():
    locator_domain = "https://www.zegna.com/"
    base_url = "https://storelocator-webservice.zegna.com/ws/REST/V8/storeList.php?country_id=US&r=8000000&displayCountry=US&language=EN"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            _city = "-".join(_["CITY"].strip().split(" "))
            _address = "-".join(_["ADDRESS"].strip().split(" ")).replace("#", "")
            page_url = f"https://www.zegna.com/us-en/store-locator/store-detail/united-states/{_city}/{_address}.{_['STORE_ID']}/"
            hours = []
            for hh in _["OPENING_HOURS"].split(","):
                try:
                    if not hh:
                        continue
                    day = hh.split(":")[0]
                    times = " ".join(hh.split(":")[1:])
                    hours.append(f"{hours_object[day]}: {times}")
                except:
                    hours = ["temporarily closed"]

            yield SgRecord(
                page_url=page_url,
                location_name=_["NAME"],
                store_number=_["STORE_ID"],
                street_address=_["ADDRESS"],
                city=_["CITY"],
                state=_["STATE"],
                zip_postal=_["POSTAL_CODE"],
                latitude=_["LATITUDE"],
                longitude=_["LONGITUDE"],
                country_code=_["COUNTRY"],
                phone=_["PHONE_NUMBER"].split("ext")[0].strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
