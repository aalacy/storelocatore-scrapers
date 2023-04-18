from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.thenorthface.com.mx"
base_url = "https://thenorthfacemx.vtexassets.com/_v/public/assets/v1/published/bundle/public/react/asset.min.js?v=1&files=thenorthfacemx.store-finder@0.3.12,common,0,Map&files=vtex.sticky-layout@0.3.4,common,0,StickyLayout&files=vtex.react-portal@0.4.1,common,0,Overlay&files=vtex.native-types@0.8.0,common,IOMessage,formatIOMessage,IOMessageWithMarkers&files=vtex.order-manager@0.11.1,common,0,OrderForm,OrderQueue&files=vtex.store-resources@0.86.0,common,0,MutationAddToCart,1&async=2&workspace=master"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("e.exports=JSON.parse('")[1]
            .split("},340")[0]
            .strip()[:-2]
        )["features"]
        for _ in locations:
            raw_address = _["DIRECCION"]
            addr = parse_address_intl(raw_address)
            city = addr.city
            if "CDMX" in raw_address:
                city = "CDMX"
            state = addr.state
            if "estado de méxico" in raw_address.lower():
                state = "Estado De México"
            street_address = addr.street_address_1 or ""
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            street_address = street_address.replace("Estado De México", "").strip()
            if street_address.isdigit():
                street_address = raw_address.split(",")[0].strip()
                if city:
                    street_address = street_address.split(city)[0].strip()

            yield SgRecord(
                page_url="https://www.thenorthface.com.mx/tiendas",
                location_name=_["TIENDA"],
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=addr.postcode,
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="MX",
                location_type=_["CLIENTE"],
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
