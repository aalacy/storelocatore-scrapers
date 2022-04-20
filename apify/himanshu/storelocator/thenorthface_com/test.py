from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgzip.dynamic import  Grain_8
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from sglogging import SgLogSetup
from urllib.parse import urlencode

logger = SgLogSetup().get_logger("")

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
}

header1 = {
    "Accept": "text/javascript, text/html, application/xml, text/xml, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Host": "hosted.where2getit.com",
    "Referer": "https://hosted.where2getit.com/northfaceeu/index_eu_de_responsive.html?form=locator_search&addressline=Berlin&country=DE",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
    "X-Prototype-Version": "1.7.2",
    "X-Requested-With": "XMLHttpRequest"
}

locator_domain = "https://www.thenorthface.com"
us_app_key_url = "https://hosted.where2getit.com/northface/2015/index.html"
global_app_key_url = "https://www.thenorthface.co.uk/store-locator.html"
count_url = "https://hosted.where2getit.com/northfaceeu/ajax?lang=de_AT&xml_request=%3Crequest%3E%3Cappkey%3E{}%3C%2Fappkey%3E%3Cformdata+id%3D%22getlist%22%3E%3Cobjectname%3EAccount%3A%3ACountry%3C%2Fobjectname%3E%3Cwhere%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E"


def _cmap(country):
    c_map_dict = {
        "gb": "uk"
    }
    return c_map_dict[country].upper() if c_map_dict.get(country) else country.upper()


def get_us_app_key():
    with SgRequests() as session:
        app_key_request = session.get(us_app_key_url)
        app_key_soup = bs(app_key_request.text, "lxml")
        app_key = "C1907EFA-14E9-11DF-8215-BBFCBD236D0E"
        for script in app_key_soup.find_all("script"):
            if "appkey: " in script.text:
                app_key = (
                    script.text.split("appkey: ")[1].split(",")[0].replace("'", "")
                )
                break
        
        return app_key

def get_global_app_key():
    with SgRequests() as session:
        app_key_request = session.get(us_app_key_url)
        try:
            app_key  = app_key_request.text.replace('"w2giKey":')[1].split(",").strip()[1:-1]
        except:
            app_key = "3A992F50-193E-11E5-91BC-C90E919C4603"
        return app_key

def calc_count(app_key):
    with SgRequests() as session:
        total = 0
        countries = bs(session.get(count_url.format(app_key), headers=header1).text, "lxml").select('account_country')
        for country in countries:
            cnt = int(country.description_count.text.split("(")[1].split(")")[0].strip())
            print(f"{country.select_one('description_count').text.split('(')[0].strip()}, ")
            total += cnt
        print(f"cuntries {len(countries)}")

class ExampleSearchIteration(SearchIteration):
    def __init__(self, app_key):
        self.app_key = app_key

    def do(
        self,
        coord,
        zipcode,
        current_country,
        items_remaining,
        found_location_at,
    ):
        with SgRequests() as session:
            params = {
                "lang": "en_GB",
                "xml_request": f'<request><appkey>3A992F50-193E-11E5-91BC-C90E919C4603</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><order>rank,_distance</order><searchradius>25</searchradius><radiusuom>km</radiusuom><geolocs><geoloc><addressline>{str(zipcode)}</addressline><longitude></longitude><latitude></latitude><country>{_cmap(current_country)}</country></geoloc></geolocs><where><or><northface><eq></eq></northface><retailstore><eq></eq></retailstore><outletstore><eq></eq></outletstore></or><and><or><youth><eq></eq></youth><apparel><eq></eq></apparel><mountain_athletics><eq></eq></mountain_athletics><footwear><eq></eq></footwear><equipment><eq></eq></equipment><summit><eq></eq></summit><mt><eq></eq></mt></or></and></where></formdata></request>'
                # "xml_request": f'<request><appkey>{self.app_key}</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><order>rank,_distance</order><searchradius>200</searchradius><radiusuom>mi</radiusuom><geolocs><geoloc><addressline>{str(zipcode)}</addressline><longitude></longitude><latitude></latitude><country>{current_country.upper()}</country></geoloc></geolocs><where><or><northface><eq></eq></northface><retailstore><eq></eq></retailstore><outletstore><eq></eq></outletstore></or><and><or><youth><eq></eq></youth><apparel><eq></eq></apparel><mountain_athletics><eq></eq></mountain_athletics><footwear><eq></eq></footwear><equipment><eq></eq></equipment><summit><eq></eq></summit><mt><eq></eq></mt></or></and></where></formdata></request>'
            }
            r = session.get(
                f"https://hosted.where2getit.com/northfaceeu/ajax?{urlencode(params)}",
                headers=headers
            )
            locations = bs(r.text, 'lxml').select('poi')
            logger.info(f"[{current_country}] {coord[0], coord[1]} found: {len(locations)}")
            if len(locations) > 0:
                import pdb; pdb.set_trace()
            for _ in locations:
                page_url = "https://www.thenorthface.com/utility/store-locator.html"
                if _["country"] == "CA":
                    page_url = (
                        "https://www.thenorthface.com/en_ca/utility/store-locator.html"
                    )
                storekey = _["clientkey"]
                if storekey and "USA" in "".join(storekey):
                    page_url = (
                        "https://stores.thenorthface.com/"
                        + "".join(_["state"]).lower()
                        + "/"
                        + "".join(_["city"]).replace(" ", "-").lower()
                        + "/"
                        + storekey
                    )
                street_address = ""
                if _["address1"] is not None:
                    street_address = street_address + _["address1"]
                if _["address2"] is not None:
                    street_address = street_address + _["address2"]
                if street_address == "":
                    continue

                state = _["state"] if _["country"] == "US" else _["province"]
                location_type = "the north face"
                north_store = _.get("northface")
                if north_store == "1":
                    location_type = "the north face store"
                outlet_store = _.get("outletstore")
                if outlet_store == "1":
                    location_type = "the north face outletstore"

                phone = (
                    _["phone"].split("or")[0].split(";")[0].split("and")[0]
                    if _["phone"] is not None and _["phone"] != "TBD"
                    else "<MISSING>"
                )

                hours = ""
                if _["m"] is not None:
                    hours = hours + " Monday " + _["m"]
                if _["t"] is not None:
                    hours = hours + " Tuesday " + _["t"]
                if _["w"] is not None:
                    hours = hours + " Wednesday " + _["w"]
                if _["thu"] is not None:
                    hours = hours + " Thursday " + _["thu"]
                if _["f"] is not None:
                    hours = hours + " Friday " + _["f"]
                if _["sa"] is not None:
                    hours = hours + " Saturday " + _["sa"]
                if _["su"] is not None:
                    hours = hours + " Sunday " + _["su"]

                found_location_at(_["latitude"], _["longitude"])
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["name"],
                    street_address=street_address,
                    city=_["city"],
                    state=state,
                    zip_postal=_["postalcode"],
                    country_code=_["country"],
                    phone=phone,
                    location_type=location_type,
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    locator_domain=locator_domain,
                    hours_of_operation=hours,
                )


if __name__ == "__main__":
    with SgRequests() as session:
        global_app_key = get_global_app_key()
        # calc_count(global_app_key)
        app_key = get_us_app_key()
        with SgWriter(
            SgRecordDeduper(
                SgRecordID(
                    {
                        SgRecord.Headers.LATITUDE,
                        SgRecord.Headers.LONGITUDE,
                        SgRecord.Headers.PAGE_URL,
                    }
                ),
                duplicate_streak_failure_factor=1000,
            )
        ) as writer:
            search_maker = DynamicSearchMaker(
                search_type="DynamicZipSearch", granularity=Grain_8()
            )
            search_iter = ExampleSearchIteration(app_key=get_global_app_key)
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=['gb'],
            )

            for rec in par_search.run():
                if rec:
                    writer.write_row(rec)

            
