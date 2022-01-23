from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.reebok.com/"
base_url = "https://placesws.adidas-group.com/API/search?brand=reebok&geoengine=google&method=get&category=store&latlng=37.09024%2C-95.712891&page=1&pagesize=100000&fields=name%2Cstreet1%2Cpostal_code%2Ccity%2Cphone%2Cemail1%2Clatitude_google%2Clongitude_google%2Cstoretype%2Cfactory_outlet%2Cbrand_store%2Coriginals%2Cperformance%2Cslvr%2Cneo_label%2Cy3%2Cslvr%2Cwoman%2Cfootwear%2Cfootball%2Cbasketball%2Coutdoor%2Cporsche_design%2Cmiadidas%2Cmiteam%2Cstella_mccartney%2Ceyewear%2Cmicoach%2Copening_ceremony%2Copeninghours_Monday%2Copeninghours_Tuesday%2Copeninghours_Wednesday%2Copeninghours_Thursday%2Copeninghours_Friday%2Copeninghours_Saturday%2Copeninghours_Sunday%2Coperational_status%2Cfrom_date%2Cto_date%2Cdont_show_country%2CCnC%2Cela%2Crun_genie%2Cgift_wrapping%2Cmi_adidas%2Cshoe_lasering%2Cflocking%2Cfood_nutrition%2Cconfirmed_app%2Cgift_cards%2Cfree_wifi%2Ctake_back_program&format=json&storetype=&tagging="
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(session.get(base_url, headers=_headers).text)[
            "wsResponse"
        ]["result"]
        for _ in locations:
            hours = []
            for day in days:
                if _.get(f"openinghours_{day}"):
                    hours.append(f'{day}: {_.get(f"openinghours_{day}")}')
            zip_postal = _.get("postal_code")
            if zip_postal == "n/a":
                zip_postal = ""
            yield SgRecord(
                page_url="https://www.reebok.com/us/store-locator",
                store_number=_["id"],
                location_name=_["name"],
                street_address=_.get("street1"),
                city=_["city"],
                state=_.get("state"),
                zip_postal=_.get("postal_code"),
                latitude=_.get("latitude_google"),
                longitude=_.get("longitude_google"),
                country_code=_["country"],
                phone=_.get("phone"),
                locator_domain=locator_domain,
                location_type=_.get("storetype"),
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
