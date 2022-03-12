from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch, Grain_1_KM
from sglogging import SgLogSetup
import dirtyjson as json
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("aldi")
locator_domain = "https://www.aldi.com.au/"
base_url = "https://www.yellowmap.de/Presentation/AldiSued/en-AU/ResultList?callback=jQuery20305313334830145355_1631295791192&LocX=&LocY=&HiddenBranchCode=&BranchCode=&Lux={}&Luy={}&Rlx={}&Rly={}&ZoomLevel=14&Mode=None&Filters.OPEN=false&Filters.ASxFIWI%26ASxFIBE=false&Filters.ASxFIWC=false&Filters.ASxFIPA=false&_=1631295791198"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_records(search):
    maxZ = search.items_remaining()

    for lat, lng in search:
        with SgRequests(proxy_country="us") as http:
            if search.items_remaining() > maxZ:
                maxZ = search.items_remaining()
            lng1 = lng - 0.10265350341
            lat1 = lat + 0.08370399797
            progress = (
                str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
            )

            res = http.get(base_url.format(lng1, lat1, lng, lat), headers=headers)
            if res.status_code != 200:
                logger.info(f"[{lat}, {lng}] [{progress}] ================ ")
                continue
            locations = bs(
                json.loads(
                    res.text.split("jQuery20305313334830145355_1631295791192(")[
                        1
                    ].strip()[:-1]
                )["Container"],
                "lxml",
            ).select("li.resultItem")
            logger.info(f"[{lat}, {lng}] [{progress}] [{len(locations)}]")
            if locations:
                search.found_location_at(lat, lng)
            for _ in locations:
                info = json.loads(_["data-json"].replace("&quot;", '"'))
                raw_address = (
                    " ".join(_.address.stripped_strings).replace("\n", " ").strip()
                )
                hours = []
                for hh in info["openingHours"]:
                    hours.append(f"{hh['day']['text']}: {hh['from']} - {hh['until']}")
                phone = ""
                if _.select_one("div.resultItem-Phone"):
                    phone = _.select_one("div.resultItem-Phone").text.strip()
                city_zip = _.select_one('div[itemprop="addressLocality"]').text.strip()
                yield SgRecord(
                    page_url="https://storelocator.aldi.com.au/Presentation/AldiSued/en-au/Start",
                    location_name=_.select_one(
                        "strong.resultItem-CompanyName"
                    ).text.strip(),
                    street_address=_.select_one(
                        'div[itemprop="streetAddress"]'
                    ).text.strip(),
                    city=" ".join(city_zip.split()[:-1]),
                    zip_postal=city_zip.split()[-1],
                    latitude=info["locY"],
                    longitude=info["locX"],
                    country_code=info["countryCode"].split("-")[-1],
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.AUSTRALIA], granularity=Grain_1_KM()
    )
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS}),
            duplicate_streak_failure_factor=20,
        )
    ) as writer:
        for rec in fetch_records(search):
            writer.write_row(rec)
