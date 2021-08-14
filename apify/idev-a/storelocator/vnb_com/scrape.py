from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("vnb")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


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
    locator_domain = "https://www.vnb.com/"
    base_url = (
        "https://www.vnb.com/index.php/contact/locations/office-locations-directions"
    )
    atm_url = "https://www.vnb.com/index.php/contact/atm-locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        banks = soup.select("div.section div.section")
        logger.info(f"{len(banks)} found")
        for _ in banks:
            addr = list(_.select_one("div.location-text p").stripped_strings)
            try:
                coord = _.a["href"].split("/@")[1].split("/data")[0].split(",")
            except:
                try:
                    coord = _.a["href"].split("!3d")[1].split("!3m")[0].split("!4d")
                except:
                    try:
                        coord = _.a["href"].split("ll=")[1].split("&")[0].split(",")
                    except:
                        coord = ["", ""]

            phone = ""
            blocks = list(_.select_one("div.location-text").stripped_strings)[1:-1]
            hours_of_operation = ""
            for x, aa in enumerate(blocks):
                if len(blocks) > 2 and _p(aa):
                    phone = aa
                    if len(blocks) > 3:
                        hours = blocks[x + 1 :]
                        if hours[-1].startswith("Drive-Thru Hours"):
                            del hours[-1]
                        if "Temporarily Drive-Thru Only" in hours[-1]:
                            del hours[-1]
                        if "lobby temporarily closed" in hours[0]:
                            hours_of_operation = "Temporarily CLOSED"
                        hours_of_operation = "; ".join(hours)
                    break
            hours_of_operation = (
                hours_of_operation.split("Hours:")[-1]
                .replace(",", ";")
                .replace("–", "-")
            )
            yield SgRecord(
                page_url=base_url,
                location_name=_.h2.text.strip(),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                location_type="bank",
                hours_of_operation=hours_of_operation,
            )

        sp1 = bs(session.get(atm_url, headers=_headers).text, "lxml")
        sibs = sp1.select("div#content div.section p")
        logger.info(f"{len(sibs[:-1])} found")
        for _ in sibs[1:-3]:
            if not _.text.strip():
                continue
            addr = list(_.stripped_strings)
            if "Back to top" in addr[0] or "please visit" in addr[0]:
                continue
            yield SgRecord(
                page_url=atm_url,
                location_name=addr[0],
                street_address=addr[1],
                city=addr[2].split(",")[0].strip(),
                state=addr[2]
                .replace("\xa0", " ")
                .split(",")[1]
                .strip()
                .split(" ")[0]
                .strip(),
                zip_postal=addr[2]
                .replace("\xa0", " ")
                .split(",")[1]
                .strip()
                .split(" ")[-1]
                .strip(),
                country_code="US",
                locator_domain=locator_domain,
                location_type="atm",
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
