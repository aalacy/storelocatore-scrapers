from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("pizzatwist")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://pizzatwist.com/"
base_url = "https://pizzatwist.com/"


def fetch_data():
    with SgRequests(verify_ssl=False) as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.main_popular div.p_card div.col-lg-6.col-md-6")

        for _ in locations:
            if "Coming Soon" in _.select_one("a.card_btn").text:
                continue
            _addr = [aa.text.strip() for aa in _.select("p.desc")]
            addr = parse_address_intl(" ".join(_addr))
            page_url = _.select_one("a.card_btn")["href"].strip()
            if page_url.endswith("pizzatwist.com/"):
                page_url += "home"
            logger.info(page_url)
            hours = []
            coord = ["", ""]
            phone = ""
            street_address = _addr[0]
            try:
                accountId = page_url.split("accountId=")[1].split("&")[0]
            except:
                accountId = ""
            if accountId:
                locationId = page_url.split("locationId=")[1].split("&")[0]
                url = f"https://orderonline.granburyrs.com/slice/account/initialize?account={accountId}"
                for loc in session.get(url, headers=_headers).json()["restaurants"]:
                    if loc["objectId"] == locationId:
                        street_address = loc["address"]["addressLine"]
                        if loc["address"]["addressLine2"]:
                            street_address += " " + loc["address"]["addressLine2"]
                        coord = [loc["latitude"], loc["longitude"]]
                        phone = loc["address"]["phone"]
                        if loc["hours"].get("default", {}).get("ranges"):
                            for day, hh in loc["hours"]["default"]["ranges"].items():
                                for hr in hh:
                                    hours.append(
                                        f"{day}: {hr['startString']}-{hr['endString']}"
                                    )
                        break
            else:
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                if sp1.find("b", string=re.compile(r"Store Hours", re.IGNORECASE)):
                    for hh in (
                        sp1.find("b", string=re.compile(r"Store Hours"))
                        .find_parent()
                        .find_next_sibling("table")
                        .select("tr")
                    ):
                        if not hh.text.strip():
                            continue
                        td = list(hh.stripped_strings)
                        hours.append(f"{td[0]}: {''.join(td[1:])}")
                if sp1.select_one("div.map-div img"):
                    coord = (
                        sp1.select_one("div.map-div img")["src"]
                        .split("?center=")[1]
                        .split("&")[0]
                        .split(",")
                    )
                if sp1.find("a", href=re.compile(r"tel:")):
                    phone = sp1.find("a", href=re.compile(r"tel:")).text.strip()

            yield SgRecord(
                page_url=page_url,
                location_name=_.h3.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                latitude=coord[0],
                longitude=coord[1],
                raw_address=" ".join(_addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.CITY,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
