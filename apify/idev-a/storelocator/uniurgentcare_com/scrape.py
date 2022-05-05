from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://uniurgentcare.com/"
base_url = "https://uniurgentcare.com/locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.row_inner div.tf_box")
        for _ in locations:
            if not _.h3:
                continue

            page_url = _.a["href"]
            if _.select('div.tb_text_wrap div[dir="ltr"]'):
                addr = [
                    aa.text.strip()
                    for aa in _.select('div.tb_text_wrap div[dir="ltr"]')
                ]
            else:
                addr = list(_.p.stripped_strings)
            _hr = _.find("", string=re.compile(r"HOURS:"))
            hours = []
            if _hr:
                for hh in list(_hr.find_parent().find_parent().stripped_strings):
                    if "Dec" in hh or "Jan" in hh or "hours" in hh.lower():
                        continue
                    hours.append(hh)
            try:
                coord = _.p.a["href"].split("&sll=")[1].split("&")[0].split(",")
            except:
                try:
                    coord = _.p.a["href"].split("/@")[1].split("/data")[0].split(",")
                except:
                    coord = ["", ""]

            phone = ""
            if _.h3:
                phone = _.h3.text.strip()

            yield SgRecord(
                page_url=page_url,
                location_name=_.h1.text.strip().replace("–", "-"),
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
