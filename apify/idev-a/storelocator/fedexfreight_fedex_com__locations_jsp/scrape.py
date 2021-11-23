from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgselenium import SgChrome
import re
import dirtyjson as json
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("fedexfreight")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.fedexfreight.fedex.com"
base_url = "https://www.fedexfreight.fedex.com/locations.jsp"
url = "https://www.fedexfreight.fedex.com/populateStateDropDownForOpco.do?opco=fxf&country={}"


def fetch_data():
    with SgChrome() as driver:
        with SgRequests() as session:
            driver.get(base_url)
            soup = bs(driver.page_source, "lxml")
            countries = [
                cc["value"] for cc in soup.select("select#shipperCountryCode2 option")
            ]
            for cc in countries:
                keys = json.loads(
                    session.get(url.format(cc), headers=_headers).text.strip()
                )["resultList"]
                for key in keys:
                    if not key["key"]:
                        continue
                    sp1 = bs(
                        session.get(
                            f"https://www.fedexfreight.fedex.com/locationsAll.do?opco=&shipperCountryCode={cc}&shipperStateList={key['key']}&viewList=View+listings"
                        ).text,
                        "lxml",
                    )
                    links = sp1.select("table.grid tr")
                    logger.info(f"[{cc}] [{key['key']}] {len(links)} found")
                    for link in links:
                        if link.th:
                            continue
                        td = link.select("td")
                        page_url = locator_domain + td[-1].a["href"]
                        logger.info(page_url)
                        sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                        addr = list(td[-1].stripped_strings)
                        phone = ""
                        if sp1.find("", string=re.compile(r"Phone")):
                            phone = (
                                sp1.find("", string=re.compile(r"Phone"))
                                .split(":")[-1]
                                .split("Fax")[0]
                                .strip()
                            )
                            if not phone:
                                phone = (
                                    sp1.find("", string=re.compile(r"Phone"))
                                    .find_parent("td")
                                    .find_next_sibling()
                                    .text.split("(")[0]
                                    .strip()
                                )
                        yield SgRecord(
                            page_url=page_url,
                            location_name=td[1].text.strip(),
                            street_address=addr[0],
                            city=addr[1].split(",")[0].strip(),
                            state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                            zip_postal=" ".join(
                                addr[1].split(",")[1].strip().split(" ")[1:]
                            ),
                            country_code=cc,
                            phone=phone.replace("..", ""),
                            locator_domain=locator_domain,
                        )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
