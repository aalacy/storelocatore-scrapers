from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries, Grain_2
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from typing import Iterable, Tuple, Callable
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
import dirtyjson as json
import re
from tenacity import retry, stop_after_attempt, wait_fixed

logger = SgLogSetup().get_logger("golftec")
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}
locator_domain = "https://www.golftec.com"
china_url = "https://www.golftec.cn/golf-lessons/nanshan"
jp_url = "https://golftec.golfdigest.co.jp/"


def fetch_cn(http, url):
    logger.info(url)
    res = http.get(url, headers=headers)
    sp1 = bs(res.text, "lxml")
    ss = json.loads(sp1.find("script", type="application/ld+json").string)
    raw_address = (
        sp1.find("p", string=re.compile(r"地址")).text.replace("地址", "").replace("：", "")
    )
    city = "市" + raw_address.split("市")[0]
    street_address = raw_address.split("市")[-1]
    hours = [
        ": ".join(hh.stripped_strings)
        for hh in sp1.select("div.center-details__hours ul li")
    ]
    yield SgRecord(
        page_url=url,
        location_name=ss["name"],
        street_address=street_address,
        city=city,
        country_code="China",
        latitude=ss["geo"]["latitude"],
        longitude=ss["geo"]["longitude"],
        phone=ss["contactPoint"]["telephone"],
        hours_of_operation="; ".join(hours),
        locator_domain="https://www.golftec.cn",
        raw_address=raw_address,
    )


def fetch_jp(http, url):
    logger.info(url)
    res = http.get(url, headers=headers)
    sp1 = bs(res.text, "lxml")
    links = sp1.select("dl.p-footer__salesWrap dd")[0].select(
        "ul.p-footer__store li.p-footer__store-list a"
    )
    for link in links:
        if "sec01" in link["href"]:
            continue
        page_url = "https://golftec.golfdigest.co.jp" + link["href"]
        logger.info(page_url)
        sp2 = bs(http.get(page_url, headers=headers).text, "lxml")
        s_data = json.loads(sp2.find("script", type="application/ld+json").string)
        raw_address = (
            " ".join(sp2.select_one("p.studioAccess__detail__adress").stripped_strings)
            .replace("〒", "")
            .strip()
        )
        zip_postal = raw_address.split()[0]
        s_c = " ".join(raw_address.split()[1:])
        ss = state = city = street_address = ""
        if "都" in s_c:
            ss = s_c.split("都")[-1]
            state = s_c.split("都")[0] + "都"
        elif "県" in s_c:
            ss = s_c.split("県")[-1]
            state = s_c.split("県")[0] + "県"
        elif "府" in s_c:
            ss = s_c.split("府")[-1]
            state = s_c.split("府")[0] + "府"

        if "市" in ss:
            city = ss.split("市")[0] + "市"
            street_address = ss.split("市")[-1]
        else:
            street_address = ss

        hours = sp2.select_one(
            "dl.p-studioInfo__desc.-businessHours dd.p-studioInfo__desc__content"
        ).text.strip()
        coord = (
            sp2.select_one("p.studioAccess__detail__map")
            .iframe["src"]
            .split("!1d")[1]
            .split("!2m")[0]
            .split("!3m")[0]
            .split("!3d")
        )
        yield SgRecord(
            page_url=page_url,
            location_name=s_data["name"],
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code="JP",
            latitude=coord[1],
            longitude=coord[0],
            phone=s_data["telephone"],
            hours_of_operation=hours,
            locator_domain="https://golftec.golfdigest.co.jp",
            raw_address=raw_address,
        )


@retry(wait=wait_fixed(1), stop=stop_after_attempt(2))
def get_locs(http, url):
    res = http.get(url, headers=headers)
    return res.json()


class ExampleSearchIteration(SearchIteration):
    def do(
        self,
        coord: Tuple[float, float],
        zipcode: str,
        current_country: str,
        items_remaining: int,
        found_location_at: Callable[[float, float], None],
    ) -> Iterable[SgRecord]:
        # Need to add dedupe. Added it in pipeline.
        maxZ = items_remaining

        lat = coord[0]
        lng = coord[1]
        with SgRequests(proxy_country="us") as http:
            if items_remaining > maxZ:
                maxZ = items_remaining
            url = f"https://wcms.golftec.com/loadmarkers_6.php?thelong={lng}&thelat={lat}&georegion=North+America&pagever=prod&maptype=closest10"

            try:
                locations = get_locs(http, url)
            except:
                logger.info(f"[{lat}, {lng}] failed")
                locations = {}

            if "centers" in locations:
                found_location_at(lat, lng)
                for _ in locations["centers"]:
                    page_url = f"{locator_domain}{_['link']}"
                    res = http.get(page_url, headers=headers)
                    if res.status_code != 200:
                        continue
                    soup = bs(res.text, "lxml")
                    street_address = _["street1"]
                    if _["street2"]:
                        street_address += " " + _["street2"]
                    if street_address and "coming soon" in street_address.lower():
                        continue
                    hours = [
                        ": ".join(hh.stripped_strings)
                        for hh in soup.select(
                            "div.center-details__hours div.seg-center-hours ul li"
                        )
                    ]
                    if not hours:
                        hours = [
                            ": ".join(hh.stripped_strings)
                            for hh in soup.select("div.center-details__hours ul li")
                        ]
                    yield SgRecord(
                        page_url=page_url,
                        store_number=_["cid"],
                        location_name=_["name"],
                        street_address=street_address.replace(
                            "Inside Golf Town", ""
                        ).strip(),
                        city=_["city"],
                        state=_["state"],
                        zip_postal=_["zip"],
                        country_code=_["country"],
                        phone=_["phone"],
                        hours_of_operation="; ".join(hours),
                        locator_domain=locator_domain,
                    )

                progress = str(round(100 - (items_remaining / maxZ * 100), 2)) + "%"

                logger.info(
                    f"[{lat}, {lng}] [{len(locations['centers'])}] | [{progress}]"
                )


if __name__ == "__main__":
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch", granularity=Grain_2()
    )
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=1500
        )
    ) as writer:
        with SgRequests(proxy_country="us") as http:
            for rec in fetch_cn(http, china_url):
                writer.write_row(rec)

            for rec in fetch_jp(http, jp_url):
                writer.write_row(rec)

            search_iter = ExampleSearchIteration()
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=[
                    SearchableCountries.USA,
                    SearchableCountries.CANADA,
                    SearchableCountries.SINGAPORE,
                ],
            )

            for rec in par_search.run():
                writer.write_row(rec)
