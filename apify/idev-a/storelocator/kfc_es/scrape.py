from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kfc")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kfc.es"
base_url = "https://api.kfc.es/configurations"


def has_zipcode(val):
    zip_postal = None
    for zz in val.split():
        if zz.strip().isdigit() and len(zz.strip()) > 3:
            zip_postal = zz
            break
    return zip_postal


def _r(val):
    if val.strip().endswith(","):
        return val.strip()[:-1]
    else:
        return val.strip()


def fetch_data():
    with SgRequests(proxy_country="us") as session:
        for key in session.get(base_url, headers=_headers).json()["storeKeys"]:
            url = f"https://api.kfc.es/find-a-kfc/{key}"
            try:
                locations = session.get(url, headers=_headers).json()["Value"]
            except:
                locations = []
            logger.info(f"[{key}] {len(locations)} found")
            for store in locations:
                _ = store["googleBusinessData"]
                raw_address = _r(_["address"].replace("Spain", "").strip())
                raw_address = " ".join(
                    [aa.strip() for aa in raw_address.split() if aa.strip()]
                )
                addr = [aa.strip() for aa in raw_address.split(",")]
                street_address = city = state = zip_postal = ""
                if len(addr) > 1 and addr[-1] not in [
                    "s/n",
                    "2",
                    "3",
                    "Polígono de Son Malferit",
                    "54",
                ]:
                    zip_postal = has_zipcode(addr[-1].strip())
                    if zip_postal:
                        city = (
                            addr[-1]
                            .replace(zip_postal, "")
                            .replace("16", "")
                            .replace("13", "")
                            .replace("15", "")
                            .replace("89", "")
                            .strip()
                        )
                    else:
                        state = addr[-1]
                        zip_postal = has_zipcode(addr[-2].strip())
                        if zip_postal:
                            city = addr[-2].replace(zip_postal, "").strip()

                    street_address = raw_address
                    if state:
                        street_address = _r(street_address.replace(state, "").strip())

                    if city:
                        street_address = _r(street_address.replace(city, "").strip())

                    if zip_postal:
                        street_address = _r(
                            street_address.replace(zip_postal, "").strip()
                        )
                else:
                    street_address = raw_address

                page_url = f"https://www.kfc.es/encuentra-tu-kfc/{store['primaryAttributes']['slug']}"
                hours = []
                hours.append(f"Mon: {_['mondayHours']}")
                hours.append(f"Tue: {_['tuesdayHours']}")
                hours.append(f"Wed: {_['wednesdayHours']}")
                hours.append(f"Thu: {_['thursdayHours']}")
                hours.append(f"Fri: {_['fridayHours']}")
                hours.append(f"Sat: {_['saturdayHours']}")
                hours.append(f"Sun: {_['sundayHours']}")
                yield SgRecord(
                    page_url=page_url,
                    store_number=store["primaryAttributes"]["id"],
                    location_name=store["primaryAttributes"]["name"],
                    street_address=street_address,
                    city=city.replace("16", ""),
                    state=state,
                    zip_postal=zip_postal,
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code="Spain",
                    phone=_["telephone"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
