from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://peterpiperpizza.com.mx/"
base_url = "http://peterpiperpizza.com.mx/"


def _p(val):
    if (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.sucursales ul p")
        for _ in locations:
            phone = ""
            _addr = []
            block = list(_.stripped_strings)
            temp = []
            for x, bb in enumerate(block):
                if _p(bb.split("|")[0]):
                    phone = bb.split("|")[0].strip()
                    temp = block[x + 1 :]
                    _addr = block[:x]
                    break
            hours = []
            for hh in temp:
                if "|" in hh:
                    continue
                if "Uber" in hh or "Servicio" in hh:
                    break
                hours.append(hh)

            street_address = _addr[0]
            yield SgRecord(
                page_url=base_url,
                location_name=_.find_previous_sibling("h3").text.strip(),
                street_address=street_address,
                city=_addr[1].split(",")[0].strip(),
                state=" ".join(_addr[1].split(",")[1].strip().split()[:-1]),
                zip_postal=_addr[1].split(",")[1].strip().split()[-1],
                country_code="Mexico",
                phone=phone,
                hours_of_operation="; ".join(hours),
                locator_domain=locator_domain,
                raw_address=" ".join(_addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
