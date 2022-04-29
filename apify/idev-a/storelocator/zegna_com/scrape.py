from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

hours_object = {
    "1": "Monday",
    "2": "Tuesday",
    "3": "Wednesday",
    "4": "Thursday",
    "5": "Friday",
    "6": "Saturday",
    "7": "Sunday",
}
locator_domain = "https://www.zegna.com/"
base_url = "https://www.zegna.com/us-en/store-locator/"
json_url = "https://storelocator-webservice.zegna.com/ws/REST/V8/storeList.php?country_id={}&r=8000000&displayCountry={}&language={}"


def fetch_data():
    with SgRequests() as session:
        countries = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "li.country__singleCountry"
        )
        for country in countries:
            locator_url = country.a["href"]
            c_info = country.a["href"].split("/")[-2].split("-")
            c_code = c_info[0]
            if c_code == "uk":
                c_code = "gb"
            c_lang = c_info[-1]
            locations = session.get(
                json_url.format(c_code, c_code, c_lang), headers=_headers
            ).json()
            logger.info(f"{c_code}, {len(locations)}")
            for _ in locations:
                _city = "-".join(_["CITY"].strip().split(" "))
                _address = "-".join(_["ADDRESS"].strip().split(" ")).replace("#", "")
                _country = "-".join(_["COUNTRY"].split(" "))
                page_url = f"{locator_url}store-locator/store-detail/{_country}/{_city}/{_address}.{_['STORE_ID']}/"
                hours = []
                for hh in _.get("OPENING_HOURS", "").split(","):
                    try:
                        if not hh:
                            continue
                        hr = hh.split(":")
                        day = hr[0]
                        hours.append(
                            f"{hours_object[day]}: {':'.join(hr[1:3])} - {':'.join(hr[3:])}"
                        )
                    except:
                        hours = ["temporarily closed"]

                street_address = _["ADDRESS"]
                city = _["CITY"]
                raw_address = street_address
                if _["COUNTRY"] == "SOUTH KOREA":
                    if (
                        "The Hyundai Seoul 2F" not in street_address
                        and city in street_address
                        and not street_address.startswith(city)
                    ):
                        street_address = city.join(
                            street_address.split(city)[:-1]
                        ).strip()
                        if street_address.endswith(","):
                            street_address = street_address[:-1]
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["NAME"],
                    store_number=_["STORE_ID"],
                    street_address=street_address,
                    city=city,
                    state=_.get("STATE"),
                    zip_postal=_.get("POSTAL_CODE"),
                    latitude=_["LATITUDE"],
                    longitude=_["LONGITUDE"],
                    country_code=_["COUNTRY"],
                    phone=_.get("PHONE_NUMBER", "").split("ext")[0].strip(),
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
