from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

locator_domain = "https://www.rhone.com"
page_url = "https://www.rhone.com/pages/find-retail-location"


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
        store_list = bs(session.get(page_url).text, "lxml").select(
            "div.page-content div.swiper-slide"
        )
        for _ in store_list:
            block = _.p.text.strip().split("\n")
            phone = ""
            addr = hours = []
            for x, bb in enumerate(block):
                if _p(bb):
                    phone = bb
                    addr = block[:x]
                    hours = block[x + 1 :]
                    break

            yield SgRecord(
                page_url=page_url,
                location_name=_.h5.text.strip(),
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                locator_domain=locator_domain,
                country_code="US",
                phone=phone,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
