from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.carrefour.pf"
base_url = "https://www.carrefour.pf/nos-magasins"
days = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = json.loads(soup.select_one("script#__NEXT_DATA__").string)["props"][
            "pageProps"
        ]["data"]["stores"]
        for _ in locations:
            raw_address = _["address"]
            addr = raw_address.split(",")
            hours = []
            for x, hh in _["opening_hours"].items():
                if hh and type(hh) == dict:
                    day = days[int(x.replace("day", ""))]
                    times = f"{hh['open']['hours']}:{hh['open']['mins']} - {hh['close']['hours']}:{hh['close']['mins']}"
                    hours.append(f"{day}: {times}")

            street_address = addr[0]
            if len(addr) == 2:
                street_address = ""
            yield SgRecord(
                page_url=base_url,
                location_name=_["title"],
                street_address=street_address,
                city=addr[-2].strip(),
                country_code="French Polynesia",
                phone=_["phone_number"],
                latitude=_["location"]["lat"],
                longitude=_["location"]["lng"],
                locator_domain=locator_domain,
                raw_address=raw_address,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
