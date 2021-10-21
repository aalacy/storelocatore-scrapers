from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("golftec")
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}
locator_domain = "https://www.golftec.com"
base_url = "https://www.golftec.com/sitemap-main.xml"

ca_provinces_codes = {
    "AB",
    "BC",
    "MB",
    "NB",
    "NL",
    "NS",
    "NT",
    "NU",
    "ON",
    "PE",
    "QC",
    "SK",
    "YT",
}


def _p(val):
    if (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .split("x")[0]
        .strip()
        .isdigit()
    ):
        return val.split("x")[0]
    else:
        return ""


def _ph(addr):
    phone = ""
    if _p(addr[-1]):
        phone = _p(addr[-1])
        del addr[-1]
    return phone


def fetch_records(http):
    links = bs(http.get(base_url, headers=headers).text, "lxml").select("url")
    for link in links:
        page_url = link.loc.text
        if "golf-lessons/" not in page_url:
            continue
        url = page_url.split("/")[-1]
        if url in [
            "get-started",
            "pricing",
            "plans",
            "gifts",
            "app",
            "success-stories",
            "junior",
            "putting",
            "student_stories",
            "plans-pricing",
        ]:
            continue
        logger.info(page_url)
        res = http.get(page_url, headers=headers)
        if res.status_code != 200:
            continue
        sp1 = bs(res.text, "lxml")
        if sp1.select_one("div.center-details__hours h5"):
            addr = list(sp1.select_one("div.center-details__hours h5").stripped_strings)
            phone = _ph(addr)
            street_address = " ".join(addr[:-1])
            city = addr[-1].split(",")[0].strip()
            state = addr[-1].split(",")[1].strip().split(" ")[0].strip()
            zip_postal = " ".join(addr[-1].split(",")[1].strip().split()[1:])
        elif sp1.select_one("div.center-details__details h5"):
            addr = sp1.select_one("div.center-details__details h5").text.split(",")
            zip_postal = " ".join(addr[-1].strip().split()[1:])
            state = addr[-1].strip().split()[0]
            city = addr[-2]
            street_address = ", ".join(addr[:-2])
        else:
            if sp1.select_one("a.hero-block"):
                # city or state locations
                continue
        hours = [
            ": ".join(hh.stripped_strings)
            for hh in sp1.select("div.center-details__hours div.seg-center-hours ul li")
        ]
        country_code = "US"
        try:

            if state and state in ca_provinces_codes:
                country_code = "CA"

            yield SgRecord(
                page_url=page_url,
                location_name=sp1.h1.text.strip(),
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                phone=phone,
                hours_of_operation="; ".join(hours),
                locator_domain=locator_domain,
                raw_address=" ".join(addr),
            )
        except:
            import pdb

            pdb.set_trace()


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        with SgRequests() as http:
            for rec in fetch_records(http):
                writer.write_row(rec)
