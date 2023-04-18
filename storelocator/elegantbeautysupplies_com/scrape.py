from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _phone(val):
    return (
        val.split("T")[-1]
        .replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(".", "")
        .replace(" ", "")
        .strip()
    )


def _valid(val):
    return val.replace("–", "").strip()


def fetch_data():
    locator_domain = "http://www.elegantbeautysupplies.com/"
    base_url = "http://www.elegantbeautysupplies.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select(
            "div.fusion-builder-row.fusion-row .fusion-layout-column"
        )
        for _ in locations:
            if len(_.select("p")) > 1 and (
                re.search(r"coming soon", _.select("p")[1].text, re.IGNORECASE)
                or re.search(r"opening soon", _.select("p")[1].text, re.IGNORECASE)
            ):
                continue
            block = []
            for p in _.find("h3").find_next_siblings():
                block += list(p.stripped_strings)
            addr = []
            location_type = ""
            if _.p.strong and not _phone(_.p.strong.text).isdigit():
                location_type = _.p.strong.text.strip()
                del block[-1]
            phone = ""
            hours = []
            for x, bb in enumerate(block):
                bb = bb.replace("\u200b", "")
                if _phone(bb).isdigit():
                    phone = bb.split("T.")[-1].strip().replace("\u200b", "")
                    if x + 2 <= len(block):
                        hours = block[x + 2 :]
                    addr = block[:x]
                    if len(addr) > 2:
                        del addr[0]
                    break
            if not addr:
                addr = block
            try:
                coord = _.a["href"].split("/@")[1].split(",17z/data")[0].split(",")
            except:
                coord = ["", ""]
            yield SgRecord(
                page_url=base_url,
                location_name=_.h3.text,
                street_address=addr[0].replace("\u200b", ""),
                city=addr[-1].split(",")[0].strip().replace("\u200b", ""),
                state=addr[-1]
                .split(",")[1]
                .strip()
                .split(" ")[0]
                .strip()
                .replace("\u200b", ""),
                zip_postal=addr[-1]
                .split(",")[1]
                .strip()
                .split(" ")[-1]
                .replace("\u200b", "")
                .strip(),
                phone=phone,
                location_type=location_type,
                latitude=coord[0],
                longitude=coord[1],
                country_code="US",
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours)
                .replace("–", "-")
                .replace("\u200b", ""),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
