from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("dunkindonuts")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

header1 = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded",
    "Host": "www.dunkindonuts.sa",
    "Origin": "http://www.dunkindonuts.sa",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.dunkindonuts.sa"
base_url = "http://www.dunkindonuts.sa/English/Branches/Pages/default.aspx"


def _f(name, soup):
    return soup.select_one(f"input#{name}")["value"]


def _d(link, session):
    page_url = locator_domain + link.select_one(".branch-addess-val").a["href"]
    logger.info(page_url)
    res = session.get(page_url, headers=_headers)
    try:
        sp1 = bs(res.text, "lxml")
    except:
        pass
    try:
        addr = list(sp1.select_one("div.AddressArea").stripped_strings)[1].replace(
            "\n", ""
        )
    except:
        addr = ""
    try:
        coord = res.text.split("new google.maps.LatLng(")[1].split(");")[0].split(",")
        if "." not in coord[0]:
            coord[0] = coord[0][:2] + "." + coord[0][2:]
            coord[1] = coord[1][:2] + "." + coord[1][2:]
    except:
        coord = ["", ""]
    return SgRecord(
        page_url=page_url,
        store_number=page_url.split("CustomID=")[1],
        location_name=link.select_one("div.branche-name a").text.strip(),
        street_address=addr,
        city=link.select_one("div.city-name-val").text.strip(),
        country_code="Saudi Arabia",
        locator_domain=locator_domain,
        latitude=coord[0],
        longitude=coord[1],
        hours_of_operation=link.select_one("div.branch-status-val").text.strip(),
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        branches = soup.select("div.BranchesDropDown select option")
        logger.info(f"{len(branches)} branches found")
        for branch in branches:
            if branch["value"] == "-1":
                continue
            data = {
                "_wpcmWpid": _f("_wpcmWpid", soup),
                "wpcmVal": _f("wpcmVal", soup),
                "MSOWebPartPage_PostbackSource": _f(
                    "MSOWebPartPage_PostbackSource", soup
                ),
                "MSOTlPn_SelectedWpId": _f("MSOTlPn_SelectedWpId", soup),
                "MSOTlPn_View": _f("MSOTlPn_View", soup),
                "MSOTlPn_ShowSettings": _f("MSOTlPn_ShowSettings", soup),
                "MSOGallery_SelectedLibrary": _f("MSOGallery_SelectedLibrary", soup),
                "MSOGallery_FilterString": _f("MSOGallery_FilterString", soup),
                "MSOTlPn_Button": _f("MSOTlPn_Button", soup),
                "__EVENTTARGET": _f("__EVENTTARGET", soup),
                "__EVENTARGUMENT": _f("__EVENTARGUMENT", soup),
                "__REQUESTDIGEST": _f("__REQUESTDIGEST", soup),
                "MSOSPWebPartManager_DisplayModeName": _f(
                    "MSOSPWebPartManager_DisplayModeName", soup
                ),
                "MSOSPWebPartManager_ExitingDesignMode": _f(
                    "MSOSPWebPartManager_ExitingDesignMode", soup
                ),
                "MSOWebPartPage_Shared": _f("MSOWebPartPage_Shared", soup),
                "MSOLayout_LayoutChanges": _f("MSOLayout_LayoutChanges", soup),
                "MSOLayout_InDesignMode": _f("MSOLayout_InDesignMode", soup),
                "_wpSelected": _f("_wpSelected", soup),
                "_wzSelected": _f("_wzSelected", soup),
                "MSOSPWebPartManager_OldDisplayModeName": _f(
                    "MSOSPWebPartManager_OldDisplayModeName", soup
                ),
                "MSOSPWebPartManager_StartWebPartEditingName": _f(
                    "MSOSPWebPartManager_StartWebPartEditingName", soup
                ),
                "MSOSPWebPartManager_EndWebPartEditing": _f(
                    "MSOSPWebPartManager_EndWebPartEditing", soup
                ),
                "__LASTFOCUS": _f("__LASTFOCUS", soup),
                "__VIEWSTATE": _f("__VIEWSTATE", soup),
                "__VIEWSTATEGENERATOR": _f("__VIEWSTATEGENERATOR", soup),
                "__EVENTVALIDATION": _f("__EVENTVALIDATION", soup),
                "ctl00$ctl35$g_d32be31b_e261_4dc7_a144_bd302585f5df$ddlRegions": "-1",
                "ctl00$ctl35$g_d32be31b_e261_4dc7_a144_bd302585f5df$ddlCities": "-1",
                "ctl00$ctl35$g_d32be31b_e261_4dc7_a144_bd302585f5df$ddlBranchVal": branch[
                    "value"
                ],
            }
            soup = bs(session.post(base_url, headers=header1, data=data).text, "lxml")
            links = soup.select("div.container")
            logger.info(f"[{branch['value']}] {len(links)} found")
            for link in links:
                yield _d(link, session)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            if rec:
                writer.write_row(rec)
