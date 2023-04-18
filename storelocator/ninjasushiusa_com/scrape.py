from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://ninjasushiusa.com"
base_url = "https://ninjasushiusa.com/locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.et_pb_text_inner > div.row > div.col-sm-8")
        for link in links:
            if not link.text.strip():
                continue

            try:
                coord = (
                    link.find("a", string=re.compile(r"Get Directions"))["href"]
                    .split("/@")[1]
                    .split("/data")[0]
                    .split(",")
                )
            except:
                coord = ["", ""]

            phone = ""
            if link.find("a", href=re.compile(r"tel:")):
                phone = link.find("a", href=re.compile(r"tel:")).text.strip()
            _hr = link.find("strong", string=re.compile(r"Hours:"))
            hours = []
            if _hr:
                hours = list(_hr.find_parent().stripped_strings)[1:]

            children = link.findChildren(recursive=False)
            if len(children) == 1:
                children = children[0].findChildren(recursive=False)
            if link.h3:
                children = children[0].findChildren(recursive=False)
                location_name = link.h3.text.strip()
                addr = list(link.h3.find_next_sibling().stripped_strings)
            else:
                location_name = children[0].text.replace("–", "-").strip()
                if not location_name:
                    location_name = children[1].text.replace("–", "-").strip()
                aa = children[-1]
                if not aa.text.strip():
                    aa = children[-2]
                if aa.name == "p":
                    addr = list(aa.stripped_strings)
                else:
                    addr = list(aa.p.stripped_strings)

            if not location_name:
                import pdb

                pdb.set_trace()
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=addr[0].replace(",", ""),
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
