from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://www.sunglasshut.com/AjaxSGHFindPhysicalStoreLocations?latitude=52.52&longitude=13.404954&radius=2000"

    headers = {
        "Referer": "https://www.sunglasshut.com/de/sunglasses/store-locations/map?",
        "Cookie": "cto_bundle=WqZiq18zckZGaTNqNklubVNzcGY2WENqJTJGcGVYQSUyRnUlMkZwakdoaE4zJTJCOSUyQnJZZnJYWUxuWmZ6Q3piTW00NExpUFF5VW8zNE91NXZ2OVZiRUNlS3d6JTJCSVpwT1JwMCUyRklBQyUyQjZrN3NiNlFod0F1ajBKMktieDB2cVJhSllPWkg5MVRCVHglMkZaaGhwcEN4T2V4a25nV1lwa0xpRFdsb3clM0QlM0Q; _fbp=fb.1.1634234149240.1154929020; WC_PERSISTENT=4UsYBQ1yHtirBvNy0MahPs4l4nMSzzYm9vpLSRYJDkg%3D%3B2021-10-15+00%3A22%3A47.278_1634234155302-370087_14351_-1002%2C-3%2CEUR_14351; JSESSIONID=0000E6LTIKCSpy7ktiuAZg8xWM2:1c7qtpec2; WC_SESSION_ESTABLISHED=true; WC_AUTHENTICATION_1453842725=1453842725%2CcXMMoHaURKwo7dmnqml8zQjwMlJHqMucFyQ14HXa%2FFo%3D; WC_ACTIVEPOINTER=-3%2C14351; WC_USERACTIVITY_1453842725=1453842725%2C0%2Cnull%2Cnull%2C1634234155338%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C1892784604%2CyCZsesRzegQrEvCoNQzuhMY1NOOVqfjCSnaiseUNUW9Y1avkG1J8Cham%2BqIQACTyhxN36vnkcqjqK3d7dRN1eWGCoDcImiHgbLFpl8BzHY6jPyPJ6YIx2gcNYI%2FkSiwEbV437UWMAgEorc0hi3U7PFkVndwFST7j%2B0U3HJjpR4sxfJvYhHNUeKaipctMc7cHe6q%2FXWmZuJs6VBwmU2POo0sGcBs0COkbUHWnWWWrJ%2F5JNALOZFEbsfKHx3YOOlON; TS011f624f=015966d29217d5b1582e922b9a666c1b7989c71828416bf14ba94b6e5ce6f1a074a28dc5f770e523eca40772c222cda8d7a3625b5dfce60e85093727e7c9096d26e04cc157e8d4e13ba0878342237c14bd8c494e69c8130222573d8a881948a1811fa3a6a0953c98d8eb66fc3b4ddce7e05a286ae47d01e9b4dd0a0e90a3840d2ca1cad47805423102524a9c754ff6374c3c10a2f3e46d714ab8a3eb7dd82936ccd326134b86f96c2b338c7237800ef4ac8eb186955dc56d5b8afc825c3dd1de74a88f10cbe0dd6d008587352b0026d653930624921345ed70c86c0de28a7267e235935c9bd14754be56313820a14d770345e53c9e7f712689e18e0aea24ce7bdea4a4d88a; metroCode=0; COUNTRY=UA; CATALOG_ASSORTMENT=SGH; WC_AUTHENTICATION_-1002=-1002%2C5mduE4auFesN87pDyNccBg3A3LZom4jI7UYlAbvrvHg%3D; WC_USERACTIVITY_-1002=-1002%2C14351%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C1892784604%2CWN1XjgAoo5DC0O%2FcHSZ3wKr3dh%2FI8%2BNO9z02nPfmqEPQeT8Uu7oGPEHwd%2Fe1ZxN85cIuUJQ3FwbZkjpuKoCMKanxVDHqYlLYQ7NvM6rASUFVTP0KI9fVTkxt50IHEHL4O%2FekmZAVzg102AHI3NR8Z01MObMp3rfV4W7YJqWr8aufZKfVf%2Fk%2Fxdn2FoSyAhCJmohJgsYhC8V8zo%2B03ylXXL19MSU6AsZAsMetUdxa97xB3CuOHUYN1kiw14zG0ZEj; WC_GENERIC_ACTIVITYDATA=[10097943118%3Atrue%3Afalse%3A0%3Afj7Ip5iHXcr9MCtlPdYeKjVGw2H6g6ypaLP1cwEJSak%3D][com.ibm.commerce.context.ExternalCartContext|null][com.ibm.commerce.context.entitlement.EntitlementContext|4000000000000004502%264000000000000004502%26null%26-2000%26null%26null%26null][com.ibm.commerce.store.facade.server.context.StoreGeoCodeContext|null%26null%26null%26null%26null%26null][com.ibm.commerce.catalog.businesscontext.CatalogContext|20603%26null%26false%26false%26false][CTXSETNAME|Store][com.ibm.commerce.context.base.BaseContext|14351%26-1002%26-1002%26-1][com.ibm.commerce.context.audit.AuditContext|1634234155302-370087][com.ibm.commerce.context.experiment.ExperimentContext|null][com.sgh.commerce.findinstore.context.FindInStoreDefaultStoreContext|null][com.ibm.commerce.giftcenter.context.GiftCenterContext|null%26null%26null][com.ibm.commerce.context.globalization.GlobalizationContext|-3%26EUR%26-3%26EUR]; aka-cc=UA; aka-ct=KIEV; aka-zp=; ak_bmsc=6C36606BE0413D540C2BBCC5DCCBF137~000000000000000000000000000000~YAAQVAoQAri/cll8AQAAyodUgQ3NGeQZtQnIjNjiLXRDYf0iFBk3wOO5yZP2bG5gE5aqAevLcnest5gfkY6cC0PM5KmX59HQvvgSf7UIvZauql5TbPKwfcLpvoEPP8R/WrEdpH9jO2YNbvKBWap7SQzTOxH3KQCjnDHgxUpEUNOQxKBocWl29GfJVocCpMOSJ1NygkIdYNerfpKQaId2/ZWLNMICrWo1kEzSdxa8D20WTr0waS+vTyIVqoSZGUEstRaLzwuJua/PDAbdb4pJigBWAA4vEGcGVVc9NRoCPVWlmDOL4WJ1P48F5Srz7wWPQcrcx6uDXM5mTRYFUgOEBsHgUfrKTEA0ec5caDD7klS8yRNda4lQ5GQzLiaDRTqqPy3KVqza+JfnBzJnSKWtjP1a1nqiAz2Ttmzg3/A6w9bspjjllm3LDZlSmYKd4oMkxpYf667fRXm3HBb+P2zfe4io0r0T4IiucbSPsUi5H63mRQuzvD7HK/0sFMRgmWw=; SGPF=3DAiSKCdsDh3x9YfbSIUMv2uv4_vURtFfN27Y-1iiDqXMATWi3h8-dA; forterToken=f2d85a817e574fc281e150645e29b410_1634257380469__UDF43_6; dtCookie=-21$VR3HFF723NBHLH7NIF3J3OMRKNHOSNT8; rxVisitor=1634257370850F4MBOT25O648EQB1C6ER8OI37ICU8648; dtPC=-21$457380376_559h6vMHOFOPAFTUBFTBMOQIFKPFUNKRRHFHSF-0e2; rxvt=1634259183567|1634257370852; ftr_ncd=6; __wid=512172776; dtSa=-; dtLatC=4; sgh-desktop-facet-state-plp=categoryid:undefined|gender:true|brands:partial|polarized:true|price:true|frame-shape:partial|color:true|face-shape:false|fit:false|materials:false|lens-treatment:false; sgh-desktop-facet-state-search=; mt.v=2.226799281.1634257372609; bm_sv=B90661DFD942A0431D1A974DF69E74B2~GMqwfB7I0hw08srWCzoOZiiJS8cO3n69nAPvBTDerDbVPbd4Jwk3XJCN40IRXA9Oi8XSPi4QorP7o4daGeL7BoMgoCHIWsyeQfQl+rttCp1rlOAJe/5Y5DNwr5DAcgt78rnAofoeMuK+NtsZ8esGhnFhnBZtKB5LLg7JZHV8RLg=; utag_main=v_id:017c8154886c000e8b2adc3d241f0004c0039009009dc$_sn:1$_se:3$_ss:0$_st:1634259183093$ses_id:1634257373293%3Bexp-session$_pn:2%3Bexp-session$vapi_domain:sunglasshut.com; tealium_data_session_timeStamp=1634257373355; userToken=undefined; TrafficSource_Override=1; AMCV_125138B3527845350A490D4C%40AdobeOrg=-1303530583%7CMCIDTS%7C18916%7CMCMID%7C05787876780449747262418047158326800711%7CMCAAMLH-1634862173%7C6%7CMCAAMB-1634862173%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1634264573s%7CNONE%7CMCAID%7CNONE%7CMCSYNCSOP%7C411-18923%7CvVersion%7C3.3.0; AMCVS_125138B3527845350A490D4C%40AdobeOrg=1; s_ecid=MCMID%7C05787876780449747262418047158326800711; _cs_mk=0.2828239252964845_1634257377428; s_cc=true",
    }

    r = session.get(api, headers=headers)
    js = r.json()["locationDetails"]

    for j in js:
        location_name = j.get("displayAddress")
        street_address = j.get("address")
        city = j.get("city")
        postal = j.get("zip")
        country_code = j.get("countryCode")
        phone = j.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        _tmp = []
        hours = j.get("hours") or []
        for h in hours:
            day = h.get("day")
            start = h.get("open")
            end = h.get("close")
            if not start:
                _tmp.append(f"{day}: Closed")
            else:
                _tmp.append(f"{day}: {start}-{end}")
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.sunglasshut.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
