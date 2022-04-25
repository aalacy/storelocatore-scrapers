from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json; charset=utf-8",
    "origin": "https://shopsuche.telekom.de",
    "referer": "https://shopsuche.telekom.de/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


locator_domain = "https://www.telekom.de"
base_url = "https://shopsuche.telekom.de/"

types = {
    "tsg": "Nur Telekom Shops",
}


def _hoo(days, time):
    if len(days) > 1:
        return f"{days[0]} - {days[-1]}: {time}"
    else:
        return f"{days[0]}: {time}"


def fetch_data():
    with SgRequests() as session:
        shop_url = json.loads(
            session.get(base_url).text.split("gon.data=")[1].split(";")[0]
        )["config"]["api"]["shopsUrl"]
        locations = session.get(shop_url, headers=_headers).json()
        for _ in locations:

            hours = []
            if _["opens_at"]:
                start = ":".join(_["opens_at"].split(":")[:-1])
                end = ":".join(_["closes_at"].split(":")[:-1])
                hours.append(f"Montag - Freitag: {start} - {end}")
                hours.append("Samstag - Sonntag: Geschlossen")
            if _["yext_url"]:
                hours = []
                logger.info(_["yext_url"])
                res = session.get(_["yext_url"], headers=_headers)
                if res.status_code == 200:
                    sp1 = bs(res.text, "lxml")
                    prev_time = ""
                    days = []
                    hr = sp1.select("table.c-location-hours-details tbody tr")
                    for x, tr in enumerate(hr):
                        td = tr.select("td")
                        day = td[0].text.strip()
                        time = f"{' '.join(td[1].stripped_strings)}"
                        if prev_time == time:
                            days.append(day)
                            if x == len(hr) - 1:
                                hours.append(_hoo(days, prev_time))
                            continue
                        elif prev_time:
                            hours.append(_hoo(days, prev_time))
                            days = []

                        prev_time = time
                        days.append(day)
                        if x == len(hr) - 1:
                            hours.append(_hoo(days, prev_time))

            phone = ""
            if _["phone_code"]:
                phone = _["phone_code"] + _["phone_number"]

            yield SgRecord(
                page_url=_["yext_url"] or "https://www.telekom.de/start/telekom-shops",
                store_number=_["id"],
                location_name=_["name"],
                street_address=(_["street"] + " " + _["street_number"]).strip(),
                city=_["city"],
                state=_["region"],
                zip_postal=_["postal_code"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="Germany",
                location_type=_["shop_type"],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
