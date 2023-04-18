from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch, Grain_8
from sglogging import SgLogSetup
import dirtyjson as json
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("aldi")
locator_domain = "https://www.aldi.hu"
base_url = "https://www.yellowmap.de/Presentation/AldiSued/hu-HU/ResultList?callback=jQuery20308078759286038908_1631293371816&LocX=&LocY=&HiddenBranchCode=&BranchCode=&Lux={}&Luy={}&Rlx={}&Rly={}&ZoomLevel=14&Mode=None&Filters.OPEN=false&Filters.ASxFIPA=false&Filters.ASxFIWC=false&Filters.ASxFIBA=false&Filters.ASxKAFE=false&Filters.ASxFIGS=false&Filters.ASxFIEL=false&Filters.ASxPOST=false&_=1631293371818"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def _la(val):
    return (
        val.replace("&#39;", "'")
        .replace("&#170;", "å")
        .replace("&#231;", "ç")
        .replace("&#227;", "ã")
        .replace("&#233;", "é")
        .replace("&#201;", "É")
        .replace("&#186;", "°")
        .replace("&#225;", "á")
        .replace("&#243;", "ó")
        .replace("&#234;", "ê")
        .replace("&#193;", "Á")
        .replace("&#226;", "â")
        .replace("&#250;", "ú")
        .replace("&#245;", "õ")
        .replace("&#237;", "í")
        .replace("&#160;", "")
        .replace("&#195;", "Ã")
        .replace("&#199;", "Ç")
        .replace("&#218;", "Ú")
        .replace("&#211;", "Ó")
    )


def fetch_records(http, search):
    maxZ = search.items_remaining()
    for lat, lng in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        http.clear_cookies()
        lng1 = lng - 1.64245605469
        lat1 = lat + 1.21097982903
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
        res = http.get(base_url.format(lng1, lat1, lng, lat), headers=headers)
        if res.status_code != 200:
            logger.info(f"[{lat}, {lng}] [{progress}] ================ ")
            continue
        locations = bs(
            json.loads(
                res.text.split("jQuery20308078759286038908_1631293371816(")[1].strip()[
                    :-1
                ]
            )["Container"],
            "lxml",
        ).select("li.resultItem")
        logger.info(f"[{lat}, {lng}] [{progress}] [{len(locations)}]")
        for _ in locations:
            info = json.loads(_["data-json"].replace("&quot;", '"'))
            raw_address = _.address.text.strip()
            hours = []
            for hh in info["openingHours"]:
                hours.append(f"{hh['day']['text']}: {hh['from']} - {hh['until']}")
            phone = ""
            if _.select_one("div.resultItem-Phone"):
                phone = _.select_one("div.resultItem-Phone").text.strip()
            city_zip = _.select_one('div[itemprop="addressLocality"]').text.strip()
            yield SgRecord(
                page_url="https://www.aldi.hu/uzletek/",
                location_name=_.select_one(
                    "strong.resultItem-CompanyName"
                ).text.strip(),
                street_address=_la(
                    _.select_one('div[itemprop="streetAddress"]').text.strip()
                ),
                city=" ".join(city_zip.split()[1:]),
                zip_postal=city_zip.split()[0],
                latitude=info["locX"],
                longitude=info["locY"],
                country_code=info["countryCode"].split("-")[-1],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.HUNGARY], granularity=Grain_8()
    )
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=5
        )
    ) as writer:
        with SgRequests() as http:
            for rec in fetch_records(http, search):
                writer.write_row(rec)
