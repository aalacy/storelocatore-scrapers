from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("virginactive")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

header1 = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/x-www-form-urlencoded",
    "Host": "www.virginactive.co.th",
    "Origin": "https://www.virginactive.co.th",
    "Referer": "https://www.virginactive.co.th/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.virginactive.co.th"
base_url = "https://www.virginactive.co.th/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        data = {
            "__EVENTTARGET": "ctl00$phBody$LanguageSelectorText",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": soup.select_one("input#__VIEWSTATE")["value"],
            "__VIEWSTATEGENERATOR": soup.select_one("input#__VIEWSTATEGENERATOR")[
                "value"
            ],
            "__SCROLLPOSITIONX": soup.select_one("input#__SCROLLPOSITIONX")["value"],
            "__SCROLLPOSITIONY": soup.select_one("input#__SCROLLPOSITIONY")["value"],
            "__EVENTVALIDATION": soup.select_one("input#__EVENTVALIDATION")["value"],
            "ctl00$MobileDevice": "False",
            "firstName": "",
            "lastName": "",
            "email": "",
            "tel": "",
            "street": "",
            "suburb": "",
            "state": "",
            "pcode": "",
            "nokName": "",
            "nokContact": "",
            "username": "",
            "pin": "",
        }
        session.post(base_url, headers=_headers, data=data)
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.club-list-box div.club-list-text")
        for _ in locations:
            raw_address = (
                " ".join(_.p.stripped_strings).replace("\n", "").replace("\r", " ")
            )
            addr = raw_address.split(",")
            street_address = ", ".join(addr[:-1])
            page_url = locator_domain + _.select_one("a")["href"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers).text
            coord = res.split('"initMap(')[1].split(")")[0].split(",")
            sp1 = bs(res, "lxml")
            hours = []
            for hh in sp1.select("div.club-hours p.p3body"):
                hr = " ".join(hh.stripped_strings)
                if "Holiday" in hr:
                    break
                hours.append(hr)
            phone = ""
            if _.find("a", href=re.compile(r"tel:")):
                phone = _.find("a", href=re.compile(r"tel:")).text.strip()
            yield SgRecord(
                page_url=page_url,
                location_name=_.h4.text.strip(),
                street_address=street_address,
                city=" ".join(addr[-1].strip().split()[:-1]),
                zip_postal=addr[-1].strip().split()[-1],
                country_code="Thailand",
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
