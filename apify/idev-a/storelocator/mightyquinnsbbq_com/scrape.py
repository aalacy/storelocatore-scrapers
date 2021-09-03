from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.mightyquinnsbbq.com"
base_url = "https://www.mightyquinnsbbq.com/see-our-locations/"


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("section div.col-md-6")
        for _ in locations:
            if not _.text.strip() or "COMING SOON" in _.text:
                continue
            href = _.h2.find_next_sibling().a["href"]
            try:
                coord = href.split("/@")[1].split("/data")[0].split(",")
            except:
                try:
                    coord = href.split("&query=")[1].split("&")[0].split(",")
                except:
                    try:
                        coord = href.split("/")[-1].split(",")
                        if len(coord) == 1:
                            coord = ["", ""]
                    except:
                        coord = ["", ""]

            phone = ""
            if _.find("a", href=re.compile("tel:")):
                phone = _.find("a", href=re.compile("tel:")).text.strip()
            hours = []
            for hh in _.h2.find_next_sibling().find_next_siblings("p"):
                if not hh.text.strip():
                    continue
                _hr = hh.text.strip().lower()
                if "phone" in _hr or _p(_hr):
                    continue
                if "section" in _hr or "menu" in _hr:
                    break
                hours.append(hh.text.strip())
            if _.h2.find_next_sibling("p"):
                addr = _.h2.find_next_sibling("p").text.strip().split(",")
            else:
                addr = _.h2.find_next_sibling().p.text.strip().split(",")
            state = zip_postal = ""
            if _.h2.text == "Dubai":
                country_code = "UAE"
            else:
                country_code = "US"
                state = addr[2].strip().split()[0].strip()
                zip_postal = addr[2].strip().split()[-1].strip()
                if len(addr) > 3:
                    zip_postal = addr[-1].strip()
            yield SgRecord(
                page_url=base_url,
                location_name=_.h2.text.strip(),
                street_address=addr[0],
                city=addr[1].strip(),
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("\xa0", ""),
                raw_address=", ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
