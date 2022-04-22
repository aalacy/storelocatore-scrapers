from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://federicosmexicanfood.com/wp-admin/admin-ajax.php?action=csl_ajax_search&address=&formdata=addressInput%3D&lat=33.54630817723779&lng=-112.21034200000001&options%5Bdistance_unit%5D=miles&options%5Bdropdown_style%5D=none&options%5Bignore_radius%5D=0&options%5Bimmediately_show_locations%5D=0&options%5Binitial_radius%5D=50&options%5Blabel_directions%5D=Directions&options%5Blabel_email%5D=Email&options%5Blabel_fax%5D=Fax&options%5Blabel_phone%5D=Phone&options%5Blabel_website%5D=Website&options%5Bloading_indicator%5D=&options%5Bmap_center%5D=Phoenix%2C+Arizona&options%5Bmap_center_lat%5D=33.4483771&options%5Bmap_center_lng%5D=-112.0740373&options%5Bmap_domain%5D=maps.google.com&options%5Bmap_end_icon%5D=http%3A%2F%2Ffedericosmexicanfood.com%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fbulb_azure.png&options%5Bmap_home_icon%5D=http%3A%2F%2Ffedericosmexicanfood.com%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fbulb_yellow.png&options%5Bmap_region%5D=us&options%5Bmap_type%5D=roadmap&options%5Bno_autozoom%5D=0&options%5Buse_sensor%5D=false&options%5Bzoom_level%5D=12&options%5Bzoom_tweak%5D=0&radius=5000"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["response"]

    locator_domain = "https://federicosmexicanfood.com"

    for store in stores:
        location_name = store["name"].replace("&#039;", "'")
        street_address = store["address"]
        city = store["city"]
        state = store["state"]
        zip_code = store["zip"]
        country_code = "US"
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store["phone"]
        hours_of_operation = (
            store["hours"]
            .replace("\r\n", " ")
            .split("24 Hr")[0]
            .split("Dining")[0]
            .split("Drive")[0]
            .strip()
        )
        if hours_of_operation == "Everyday":
            hours_of_operation = "Everyday 24 Hrs"

        latitude = store["lat"]
        longitude = store["lng"]
        link = "https://federicosmexicanfood.com/locations/"

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=link,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
