from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("my")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.auntieannes.com.my"
base_url = "http://www.auntieannes.com.my/location.html"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.accordion div.col3")
        for _ in locations:
            block = list(_.stripped_strings)[1:]
            hours = ""
            if "Hour" in block[-1]:
                hours = block[-1].split("Opening Hours")[-1].strip()
                if hours.startswith(":"):
                    hours = hours[1:]
                del block[-1]
            if not hours:
                temp = []
                for x, bb in enumerate(block):
                    if "Hour" in bb:
                        for hh in block[x:]:
                            _hh = hh.split("Opening Hours")[-1].strip()
                            if _hh.startswith(":"):
                                _hh = _hh[1:]
                            if _hh:
                                temp.append(_hh)
                if temp:
                    hours = "; ".join(temp)

            phone = ""
            if "Telephone" in block[-1]:
                phone = block[-1].split(":")[-1].strip()
                del block[-1]
            raw_address = (
                " ".join(block).replace("\n", "").replace("\t", "") + ", Malaysia"
            )
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            state = addr.state
            zip_postal = addr.postcode
            if "62501" in raw_address:
                zip_postal = "62501"
            city = addr.city or ""
            city = city.replace(".", "")
            if "Kualar Lumpur" in street_address:
                street_address = street_address.split(city)[0].strip()
            street_address = street_address.replace("62501", "")
            if street_address == "16 Ss" and city:
                street_address = raw_address.split(city)[0].replace("47500", "").strip()
            yield SgRecord(
                page_url=base_url,
                location_name=_.h5.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=state,
                zip_postal=zip_postal,
                country_code="MY",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
