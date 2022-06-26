from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgzip.dynamic import Grain_4
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
}

locator_domain = "https://www.thenorthface.com"
us_app_key_url = "https://www.thenorthface.co.uk/store-locator.html"
country_url = "https://hosted.where2getit.com/northfaceeu/ajax?lang=en_GB&xml_request=%3Crequest%3E%3Cappkey%3E{}%3C%2Fappkey%3E%3Cformdata+id%3D%22getlist%22%3E%3Cobjectname%3EAccount%3A%3ACountry%3C%2Fobjectname%3E%3Cwhere%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E"
json_url = "https://hosted.where2getit.com/northfaceeu/ajax?lang=en_GB&xml_request=%3Crequest%3E%3Cappkey%3E{}%3C%2Fappkey%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Corder%3Erank%2C_distance%3C%2Forder%3E%3Csearchradius%3E5000%3C%2Fsearchradius%3E%3Cradiusuom%3Emile%3C%2Fradiusuom%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3E%3C%2Faddressline%3E%3Clongitude%3E{}%3C%2Flongitude%3E%3Clatitude%3E{}%3C%2Flatitude%3E%3Ccountry%3E{}%3C%2Fcountry%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Cwhere%3E%3Cor%3E%3Cnorthface%3E%3Ceq%3E1%3C%2Feq%3E%3C%2Fnorthface%3E%3Cretailstore%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fretailstore%3E%3Coutletstore%3E%3Ceq%3E1%3C%2Feq%3E%3C%2Foutletstore%3E%3C%2For%3E%3Cand%3E%3Cor%3E%3Cyouth%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fyouth%3E%3Capparel%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fapparel%3E%3Cmountain_athletics%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fmountain_athletics%3E%3Cfootwear%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ffootwear%3E%3Cequipment%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fequipment%3E%3Csummit%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fsummit%3E%3Cmt%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fmt%3E%3C%2For%3E%3C%2Fand%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E"


def get_us_app_key():
    with SgRequests() as session:
        app_key_request = session.get(us_app_key_url, headers=headers).text
        app_key = "3A992F50-193E-11E5-91BC-C90E919C4603"
        if "w2giKey" in app_key_request:
            app_key = (
                app_key_request.split('"w2giKey":')[1].split(",")[0].replace("'", "")
            )

        return app_key


def get_countries(key):
    countries = {}
    with SgRequests() as session:
        for cc in bs(
            session.get(country_url.format(key), headers=headers).text, "lxml"
        ).select("account_country"):
            countries[cc.select_one("name").text.strip()] = cc.description.text.strip()

    return countries


def c_map(val):
    if val == "gb":
        return "UK"
    return val.upper()


def revert_c_map(val):
    if val == "UK":
        return "gb"
    return val.lower()


def _v(val):
    if val:
        return (
            val.replace("&#xa0;", " ")
            .replace("&#xa0", " ")
            .replace("&#xb0;", "°")
            .replace("&#xb4;", "'")
            .replace("&#xba;", "º")
            .replace("&#xc1;", "Á")
            .replace("&#xc2;", "Â")
            .replace("&#xc3;", "Ã")
            .replace("&#xc4;", "Ä")
            .replace("&#xc5;", "Å")
            .replace("&#xc7;", "Ç")
            .replace("&#xc8;", "È")
            .replace("&#xc9;", "É")
            .replace("&#xdf;", "ß")
            .replace("&#xdc;", "Ü")
            .replace("&#xd6;", "Ö")
            .replace("&#xd7;", "×")
            .replace("&#xd8;", "Ø")
            .replace("&#xe0;", "à")
            .replace("&#xe1;", "á")
            .replace("&#xe2;", "â")
            .replace("&#xe3;", "ã")
            .replace("&#xe4;", "ä")
            .replace("&#xe5;", "å")
            .replace("&#xe6;", "æ")
            .replace("&#xe7;", "ç")
            .replace("&#xe8;", "è")
            .replace("&#xe9;", "é")
            .replace("&#xf2;", "ò")
            .replace("&#xf3;", "ó")
            .replace("&#xf6;", "ö")
            .replace("&#xf7;", "÷")
            .replace("&#xf8;", "ø")
            .replace("&#xf9;", "ù")
            .replace("&#xf1;", "ñ")
            .replace("&#xfa;", "ú")
            .replace("&#xfb;", "û")
            .replace("&#xfc;", "ü")
            .replace("&#xfd;", "ý")
            .replace("&#x85;", "...")
            .replace("&#x92;", "'")
            .replace("&#x93;", '"')
            .replace("&#x94;", '"')
            .replace("&#x96;", "-")
            .replace("&#x9a;", "š")
            .replace("&amp;", "&")
            .strip()
        )
    else:
        return ""


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
        found_nothing,
    ):
        with SgRequests() as session:
            locations = bs(
                session.get(
                    json_url.format(
                        self.app_key, coord[1], coord[0], c_map(current_country)
                    ),
                    headers=headers,
                ).text,
                "lxml",
            ).select("poi")
            logger.info(f"[{current_country}] found: {len(locations)}")
            if len(locations) == 0:
                found_nothing()
            for _ in locations:
                page_url = "https://www.thenorthface.co.uk/store-locator.html"
                street_address = _.address1.text.strip()
                if _.address2:
                    street_address += " " + _.address2.text.strip()

                state = _.state.text.strip() if _.state else _.province.text.strip()
                location_type = ""
                north_store = _.northface.text.strip() if _.northface else ""
                if str(north_store) == "1":
                    location_type = "the north face store"
                outlet_store = _.outletstore.text.strip() if _.outletstore else ""
                if str(outlet_store) == "1":
                    location_type = "the north face outletstore"

                if not location_type:
                    icon = _.icon.text.strip() if _.icon else ""
                    if icon == "Outletstore":
                        location_type = "the north face outletstore"
                phone = (
                    _.phone.text.strip().split("or")[0].split("and")[0]
                    if _.phone is not None and _.phone.text.strip() != "TBD"
                    else "<MISSING>"
                )
                if phone == "0":
                    phone = ""

                hours = []
                if _.m and _.m.text.strip():
                    hours.append(f"Monday: {_.m.text.strip()}")
                if _.t and _.t.text.strip():
                    hours.append(f" Tuesday: {_.t.text.strip()}")
                if _.w and _.w.text.strip():
                    hours.append(f" Wednesday: {_.w.text.strip()}")
                if _.thu and _.thu.text.strip():
                    hours.append(f" Thursday: {_.thu.text.strip()}")
                if _.f and _.f.text.strip():
                    hours.append(f" Friday: {_.f.text.strip()}")
                if _.sa and _.sa.text.strip():
                    hours.append(f" Saturday: {_.sa.text.strip()}")
                if _.su and _.su.text.strip():
                    hours.append(f" Sunday: {_.su.text.strip()}")

                latitude = _.latitude.text.strip() if _.latitude else ""
                longitude = _.longitude.text.strip() if _.longitude else ""
                if latitude:
                    found_location_at(latitude, longitude)
                yield SgRecord(
                    page_url=page_url,
                    location_name=_v(_.select_one("name").text.strip()),
                    street_address=_v(street_address),
                    city=_v(_.city.text.strip()),
                    state=_v(state),
                    zip_postal=_.postalcode.text.strip(),
                    country_code=_.country.text.strip(),
                    phone=_v(phone).split(";")[0],
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    locator_domain=locator_domain,
                    hours_of_operation=_v("; ".join(hours).replace("---", ", ")),
                )


if __name__ == "__main__":
    with SgRequests() as session:
        app_key = get_us_app_key()
        countries = get_countries(app_key)
        c_list = [revert_c_map(cc) for cc in countries.keys()]
        with SgWriter(
            SgRecordDeduper(
                SgRecordID(
                    {
                        SgRecord.Headers.LATITUDE,
                        SgRecord.Headers.LONGITUDE,
                        SgRecord.Headers.PHONE,
                    }
                )
                .with_truncate(SgRecord.Headers.LATITUDE, 3)
                .with_truncate(SgRecord.Headers.LONGITUDE, 3),
                duplicate_streak_failure_factor=1000,
            )
        ) as writer:
            search_maker = DynamicSearchMaker(
                search_type="DynamicGeoSearch", granularity=Grain_4()
            )
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=lambda: ExampleSearchIteration(app_key=app_key),
                country_codes=c_list,
            )

            for rec in par_search.run():
                if rec:
                    writer.write_row(rec)
