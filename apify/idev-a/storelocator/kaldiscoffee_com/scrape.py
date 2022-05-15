from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("kaldiscoffee")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://kaldiscoffee.com"
base_url = "https://kaldiscoffee.com/pages/cafe-menus"


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
        links = soup.select("a.home-image-grid__link")
        logger.info(f"{len(links)} found")
        for link in links:
            if not link["href"].startswith("/pages/"):
                continue
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = []
            _hr = sp1.find("strong", string=re.compile(r"^Hours"))
            if _hr:
                for hh in _hr.find_parent("h6").find_next_siblings():
                    _hh = hh.text.strip()
                    if (
                        not _hh
                        or "Looking" in _hh
                        or "Click" in _hh
                        or "Get" in _hh
                        or _hh == "-"
                    ):
                        break
                    hours.append(_hh)
            else:
                _hr = sp1.find("h6", string=re.compile(r"Hours"))
                if _hr:
                    hours = [
                        hh.text.strip().split("\n")[-1]
                        for hh in _hr.find_next_siblings()
                        if hh.text.strip() and hh.text.strip().split("\n")[-1] != "-"
                    ]
                else:
                    _hr = sp1.find("", string=re.compile(r"Fall(.)hours", re.I))
                    if _hr:
                        _hp = _hr.find_parent("p")
                        if not _hp:
                            _hp = _hr.find_parent("h6")
                        if _hp:
                            for hh in _hp.find_next_siblings("p"):
                                _hh = hh.text.lower()
                                if "phone" in _hh:
                                    break
                                if "aug" in _hh or "beginning" in _hh:
                                    continue
                                hours.append("; ".join(hh.stripped_strings))
                    else:
                        _hr = sp1.find(
                            "strong", string=re.compile(r"^REGULAR HOURS:", re.I)
                        )
                        if _hr:
                            _hp = _hr.find_parent("div").find_next_sibling("div")
                            if _hp:
                                for hh in list(_hp.stripped_strings):
                                    if "Phone" in hh:
                                        break
                                    hours.append(hh)

            try:
                coord = (
                    sp1.select("iframe")[-1]["src"]
                    .split("&sll=")[1]
                    .split("&amp;")[0]
                    .split("&")[0]
                    .split(",")
                )
            except:
                try:
                    coord = (
                        sp1.select("iframe")[-1]["src"]
                        .split("!2d")[1]
                        .split("!3m")[0]
                        .split("!3d")[::-1]
                    )
                except:
                    try:
                        coord = (
                            sp1.select("iframe")[-1]["src"]
                            .split("&ll=")[1]
                            .split("&spn")[0]
                            .split(",")
                        )
                    except:
                        coord = ["", ""]
            phone = ""
            try:
                street_address = sp1.select_one(".street-address").text.strip()
                city = sp1.select_one(".locality").text.strip()
                state = sp1.select_one(".region").text.strip()
                zip_postal = sp1.select_one(".postal-code").text.strip()
                phone = sp1.select_one("span.tel").text.strip()
            except:
                if sp1.find("strong", string=re.compile(r"Address")):
                    sibling = (
                        sp1.find("strong", string=re.compile(r"Address"))
                        .find_parent()
                        .find_next_sibling()
                    )
                    if len(list(sibling.stripped_strings)) == 2:
                        aa = list(sibling.stripped_strings)
                        street_address = aa[0]
                        city = aa[1].split(",")[0].strip()
                        state = aa[1].split(",")[1].strip().split(" ")[0].strip()
                        zip_postal = aa[1].split(",")[1].strip().split(" ")[-1].strip()
                        phone = sibling.find_next_sibling("p").text.strip()
                    else:
                        if coord == ["", ""] and sibling.abbr:
                            coord = sibling.abbr["title"].split(";")
                        if sibling.select("a"):
                            street_address = sibling.select("a")[0].text.strip()
                            addr = (
                                sibling.select("a")[1].text.replace("\xa0", " ").strip()
                            )
                            city = addr.split(",")[0].strip()
                            state = addr.split(",")[1].strip().split(" ")[0].strip()
                            zip_postal = (
                                addr.split(",")[1].strip().split(" ")[-1].strip()
                            )
                            phone = list(sibling.stripped_strings)[-1]
                        else:
                            if len(list(sibling.stripped_strings)) == 1:
                                aa = list(sibling.find_next_sibling().stripped_strings)
                                street_address = aa[0]
                                city = aa[1]
                                state = aa[3]
                                zip_postal = aa[4]
                                phone = aa[6]
                            else:
                                aa = list(sibling.stripped_strings)
                                street_address = aa[-4]
                                city = aa[-3].split(",")[0].strip()
                                state = (
                                    aa[-3].split(",")[1].strip().split(" ")[0].strip()
                                )
                                zip_postal = (
                                    aa[-3].split(",")[1].strip().split(" ")[-1].strip()
                                )
                                phone = aa[-1]
                elif sp1.find("h6", string=re.compile(r"Address")):
                    sibling = sp1.find(
                        "h6", string=re.compile(r"Address")
                    ).find_next_sibling()
                    aa = list(sibling.p.stripped_strings)
                    if _p(aa[-1]):
                        phone = aa[-1]
                        del aa[-1]
                    if "map" in aa[-1].lower():
                        del aa[-1]
                    street_address = aa[-2]
                    city = aa[-1].replace("\xa0", " ").split(",")[0].strip()
                    state = (
                        aa[-1]
                        .replace("\xa0", " ")
                        .split(",")[1]
                        .strip()
                        .split(" ")[0]
                        .strip()
                    )
                    zip_postal = (
                        aa[-1]
                        .replace("\xa0", " ")
                        .split(",")[1]
                        .strip()
                        .split(" ")[-1]
                        .strip()
                    )
                elif sp1.find("p", string=re.compile(r"Address")):
                    addr = list(
                        sp1.find("p", string=re.compile(r"Address"))
                        .find_next_sibling("div")
                        .p.stripped_strings
                    )
                    street_address = " ".join(addr[:-1])
                    city = addr[-1].replace("\xa0", " ").split(",")[0]
                    state = (
                        addr[-1].replace("\xa0", " ").split(",")[-1].strip().split()[0]
                    )
                    zip_postal = (
                        addr[-1].replace("\xa0", " ").split(",")[-1].strip().split()[-1]
                    )
                else:
                    sibling = (
                        sp1.find("", string=re.compile(r"^Address"))
                        .find_parent("div")
                        .find_parent()
                        .find_next_sibling()
                    )
                    aa = list(sibling.p.stripped_strings)
                    street_address = aa[0]
                    city = aa[1].split(",")[0].strip()
                    state = aa[1].split(",")[1].strip()
                    zip_postal = aa[1].split(",")[2].strip()
            if not _p(phone):
                phone = ""
            if not phone:
                if sp1.find(
                    "strong", string=re.compile(r"Phone number", re.IGNORECASE)
                ):
                    phone = (
                        sp1.find(
                            "strong",
                            string=re.compile(r"Phone number", re.IGNORECASE),
                        )
                        .text.split(":")[-1]
                        .replace("Phone number", "")
                        .replace("\xa0", "")
                    )
                elif sp1.find("p", string=re.compile(r"Phone number", re.IGNORECASE)):
                    phone = (
                        sp1.find("p", string=re.compile(r"Phone number", re.IGNORECASE))
                        .text.split(":")[-1]
                        .replace("Phone number", "")
                        .replace("\xa0", "")
                    )
            if not zip_postal.replace("-", "").isdigit():
                zip_postal = ""

            location_type = ""
            if sp1.find("em", string=re.compile(r"temporarily closed")):
                location_type = "temporarily closed"
            hours_of_operation = (
                "; ".join(hours)
                .replace("Open", "")
                .split("Bulk")[0]
                .replace("–", "-")
                .replace("\xa0", " ")
                .replace("Normal Hours:", "")
            )
            if hours_of_operation.endswith(";"):
                hours_of_operation = hours_of_operation[:-1]
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.select_one("h1.section__title-text").text.strip(),
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="USA",
                phone=phone,
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                location_type=location_type,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
