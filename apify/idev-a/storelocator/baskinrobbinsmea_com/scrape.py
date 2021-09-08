from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.baskinrobbinsmea.com/en/delivery-service/sa/"
base_url = "https://www.baskinrobbinsmea.com/wp-admin/admin-ajax.php?action=csl_ajax_onload&address=&formdata=addressInput%3D&lat=21.082647&lng=44.528527&options%5Bdistance_unit%5D=km&options%5Bdropdown_style%5D=none&options%5Bignore_radius%5D=0&options%5Bimmediately_show_locations%5D=1&options%5Binitial_radius%5D=100000000&options%5Blabel_directions%5D=Directions&options%5Blabel_email%5D=Email&options%5Blabel_fax%5D=Fax%3A+&options%5Blabel_phone%5D=Phone%3A+&options%5Blabel_website%5D=Website&options%5Bloading_indicator%5D=&options%5Bmap_center%5D=United+Arab+Emirates&options%5Bmap_center_lat%5D=21.082647&options%5Bmap_center_lng%5D=44.528527&options%5Bmap_domain%5D=maps.google.ae&options%5Bmap_end_icon%5D=http%3A%2F%2Fwww.baskinrobbinsmea.com%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fbulb_azure.png&options%5Bmap_home_icon%5D=http%3A%2F%2Fwww.baskinrobbinsmea.com%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fbox_yellow_home.png&options%5Bmap_region%5D=ae&options%5Bmap_type%5D=&options%5Bno_autozoom%5D=0&options%5Buse_sensor%5D=false&options%5Bzoom_level%5D=4&options%5Bzoom_tweak%5D=1&radius=100000000"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["response"]
        for loc in locations:
            _ = loc["data"]
            street_address = _["sl_address"]
            if _["sl_address2"]:
                street_address += " " + _["sl_address2"]
            zip_postal = _["sl_zip"]
            country_code = _["sl_country"]
            if zip_postal == "Saudi Arabia":
                zip_postal = ""
                country_code = "Saudi Arabia"
            yield SgRecord(
                page_url="https://www.baskinrobbinsmea.com/en/store-locator/",
                store_number=_["sl_id"],
                location_name=_["sl_store"],
                street_address=street_address,
                city=_["sl_city"],
                state=_["sl_state"],
                zip_postal=zip_postal,
                latitude=_["sl_latitude"],
                longitude=_["sl_longitude"],
                country_code=country_code,
                phone=_["sl_phone"],
                locator_domain=locator_domain,
                hours_of_operation=_["sl_hours"].replace(",", ";"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
