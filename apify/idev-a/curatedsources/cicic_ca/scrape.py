from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("cicic")

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://www.cicic.ca",
    "referer": "https://www.cicic.ca/869/RepertoireEtablissements.aspx?sortcode=2.25.26.26.27.28",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.cicic.ca"


def _hidden(sp1, name):
    return sp1.select_one(f"input#{name}")["value"]


def _parse(_, session, page=1):
    td = [tt.text.strip() for tt in _.select("td")]
    page_url = locator_domain + _.a["href"]
    logger.info(page_url)
    sp3 = bs(session.get(page_url, headers=_headers).text, "lxml")
    _addr = sp3.select_one("div.postaladdress")
    if not _addr:
        return None
    addr = list(_addr.stripped_strings)
    if sp3.select_one("span#ctl12_ctl00_orgtollfree"):
        phone = sp3.select_one("#ctl12_ctl00_orgtollfree").text.strip()
    elif sp3.select_one("#ctl12_ctl00_orgphone"):
        phone = sp3.select_one("#ctl12_ctl00_orgphone").text.strip()
    else:
        phone = ""

    return SgRecord(
        page_url=page_url,
        store_number=td[0],
        location_name=td[1],
        street_address=addr[0],
        city=td[2],
        state=addr[2],
        zip_postal=td[3],
        country_code=addr[-1],
        phone=phone,
        location_type=td[-2],
        locator_domain=locator_domain,
        latitude=td[4],
        longitude=td[6],
    )


def fetch_data():
    base_url = "https://www.cicic.ca/869/results.canada?search="
    search_url = "https://www.cicic.ca/869/RepertoireEtablissements.aspx?sortcode=2.25.26.26.27.28"
    with SgRequests() as session:
        sp1 = bs(session.get(base_url).text, "lxml")
        locations = sp1.select("table.rgMasterTable > tbody tr")
        logger.info(f"[page 1] {len(locations)} found")
        for _ in locations:
            loc = _parse(_, session)
            if loc:
                yield loc
        total_page = int(
            sp1.select_one("div.rgWrap.rgInfoPart")
            .text.strip()
            .split("in")[1]
            .split("pages")[0]
            .strip()
        )
        cur_page = 1
        while cur_page < total_page:
            form_data = {
                "__EVENTTARGET": sp1.select_one("div.rgArrPart2 input")["name"],
                "__EVENTARGUMENT": "",
                "__VSTATE": _hidden(sp1, "__VSTATE"),
                "__VIEWSTATE": "",
                "__EVENTVALIDATION": _hidden(sp1, "__EVENTVALIDATION"),
                "ctl12$ctl00$EDsearchBox": "",
                "ctl12_ctl00_EDsearchBox_ClientState": '{"enabled":true,"logEntries":[{"Type":1,"Index":0,"Data":{"text":"","value":""}}]}',
                "ctl12$ctl00$gridresults$ctl00$ctl03$ctl01$PageSizeComboBox": "30",
                "ctl12_ctl00_gridresults_ctl00_ctl03_ctl01_PageSizeComboBox_ClientState": "",
                "ctl12_ctl00_gridresults_ClientState": "",
            }
            sp1 = bs(
                session.post(search_url, headers=_headers, data=form_data).text, "lxml"
            )
            cur_page = int(sp1.select_one("a.rgCurrentPage").text.strip())

            locations = sp1.select("table.rgMasterTable > tbody tr")
            logger.info(f"[page {cur_page}] {len(locations)} found")
            for _ in locations:
                loc = _parse(_, session, cur_page)
                if loc:
                    yield loc


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
