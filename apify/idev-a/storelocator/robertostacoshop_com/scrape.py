from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://robertostacoshop.com"
base_url = "https://robertostacoshop.com/locations/"


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
        locations = soup.select(
            "div.page_content_wrap div.vc_column-inner div.wpb_wrapper div.wpb_text_column div.wpb_wrapper h3"
        )
        for _ in locations:
            if _.text == "•":
                continue
            addr = list(_.stripped_strings)
            if "Coming early" in addr[0] or "Coming soon" in addr[0]:
                continue
            try:
                coord = _.a["href"].split("ll=")[1].split("&")[0].split(",")
            except:
                try:
                    coord = _.a["href"].split("/@")[1].split("/data")[0].split(",")
                except:
                    coord = ["", ""]
            location_type = ""
            if "CLOSED" in _.text:
                location_type = "CLOSED"
            hours_of_operation = phone = ""
            for aa in addr:
                if "open" in aa.lower():
                    hours_of_operation = aa.replace("(", "").replace(")", "")
                if _p(aa):
                    phone = aa
            yield SgRecord(
                page_url=base_url,
                location_name="",
                street_address=addr[0],
                city=_.find_previous_sibling("h2").text.strip(),
                state=_.find_previous_sibling("h1").text.replace(":", "").strip(),
                country_code="US",
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
