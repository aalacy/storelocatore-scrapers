from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://www.sunglasshut.com/AjaxSGHFindPhysicalStoreLocations?latitude=48.8566&longitude=2.35222&radius=2000"

    headers = {
        "Referer": "https://www.sunglasshut.com/fr/sunglasses/store-locations",
        "Cookie": "cto_bundle=WsBON18zckZGaTNqNklubVNzcGY2WENqJTJGcFc5NFZtNUtKTHExMVBIcEMlMkJCbCUyRlhESHREOG9CdTFjTFVkdXNNV1N6Y1JCWkpnMGtlTDFvd0pCbGtwJTJCSU1xMTJRQllPVFBhUG9nM0hVQnNYT1pObG56Qjh4VVc0YiUyQlRBWkhERFlNY0RwQ1NmTEltazNIb09rNUpyN0V6eXhoVkVjdFExenE2bTIwWFNERVZGcG1IZFBYaWhwaXhYUjlrQWNOc2VCZnBpVUxK; _fbp=fb.1.1634234149240.1154929020; WC_PERSISTENT=NbJxZFYbtgmoTZVyGwUwv6CUirjspFBcGiZQspIQYrs%3D%3B2021-10-15+00%3A28%3A56.273_1634234155302-370087_14351_1453854362%2C-3%2CEUR_13801_-1002%2C-2%2CEUR_13801; JSESSIONID=0000E6LTIKCSpy7ktiuAZg8xWM2:1c7qtpec2; WC_SESSION_ESTABLISHED=true; WC_AUTHENTICATION_1453842725=1453842725%2CcXMMoHaURKwo7dmnqml8zQjwMlJHqMucFyQ14HXa%2FFo%3D; WC_ACTIVEPOINTER=-2%2C13801; WC_USERACTIVITY_1453842725=1453842725%2C0%2Cnull%2Cnull%2C1634234155338%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C1892784604%2CyCZsesRzegQrEvCoNQzuhMY1NOOVqfjCSnaiseUNUW9Y1avkG1J8Cham%2BqIQACTyhxN36vnkcqjqK3d7dRN1eWGCoDcImiHgbLFpl8BzHY6jPyPJ6YIx2gcNYI%2FkSiwEbV437UWMAgEorc0hi3U7PFkVndwFST7j%2B0U3HJjpR4sxfJvYhHNUeKaipctMc7cHe6q%2FXWmZuJs6VBwmU2POo0sGcBs0COkbUHWnWWWrJ%2F5JNALOZFEbsfKHx3YOOlON; TS011f624f=015966d292bd82683852c7564ad1594d7265645c870921da8d19eb171b983f3586c66a6d59780df179c6cad5018811fa5c7bf91e2964a76513d411d6005da53e2ce73a8c757c435583420d5345377f700572f666572913649d9043f983a2b54b498b5a34d08504153dce3880ee4622ea25750405f1ec99555e6fb4a8638bf9d7a21d7ca9118264232e547fdc4818337522597fd9585c0c789e33a647f799ebbfe24f5eda104d55c84369ac7e6db45b126ec7e2883817c5fc13382cd57b64de94ed82754ed6f9cd2b57a3de4ae666fdb3326c9078640400e13b071f4bf10ebd17631e082ac913cffa3f3ced9924bd335402f52aa2d9060dc6bdab4fe5030695eccb6f9fd61a37c10167303bcd8639aac302600d53aba43611db13c1d5793cdf61bc65a9e765; metroCode=0; COUNTRY=UA; CATALOG_ASSORTMENT=SGH; aka-cc=UA; aka-ct=KIEV; aka-zp=; ak_bmsc=6C36606BE0413D540C2BBCC5DCCBF137~000000000000000000000000000000~YAAQVAoQAri/cll8AQAAyodUgQ3NGeQZtQnIjNjiLXRDYf0iFBk3wOO5yZP2bG5gE5aqAevLcnest5gfkY6cC0PM5KmX59HQvvgSf7UIvZauql5TbPKwfcLpvoEPP8R/WrEdpH9jO2YNbvKBWap7SQzTOxH3KQCjnDHgxUpEUNOQxKBocWl29GfJVocCpMOSJ1NygkIdYNerfpKQaId2/ZWLNMICrWo1kEzSdxa8D20WTr0waS+vTyIVqoSZGUEstRaLzwuJua/PDAbdb4pJigBWAA4vEGcGVVc9NRoCPVWlmDOL4WJ1P48F5Srz7wWPQcrcx6uDXM5mTRYFUgOEBsHgUfrKTEA0ec5caDD7klS8yRNda4lQ5GQzLiaDRTqqPy3KVqza+JfnBzJnSKWtjP1a1nqiAz2Ttmzg3/A6w9bspjjllm3LDZlSmYKd4oMkxpYf667fRXm3HBb+P2zfe4io0r0T4IiucbSPsUi5H63mRQuzvD7HK/0sFMRgmWw=; SGPF=3DAiSKCdsDh3x9YfbSIUMv2uv4_vURtFfN27Y-1iiDqXMATWi3h8-dA; forterToken=f2d85a817e574fc281e150645e29b410_1634257806270__UDF4_6; dtCookie=v_4_srv_3_sn_VR3HFF723NBHLH7NIF3J3OMRKNHOSNT8_app-3Ab359c07662f0b428_1_ol_0_perc_100000_mul_1; rxVisitor=1634257370850F4MBOT25O648EQB1C6ER8OI37ICU8648; dtPC=3$457805378_604h1vMHOFOPAFTUBFTBMOQIFKPFUNKRRHFHSF-0; rxvt=1634259605569|1634257370852; ftr_ncd=6; __wid=512172776; dtSa=-; dtLatC=119; sgh-desktop-facet-state-plp=categoryid:undefined|gender:true|brands:partial|polarized:true|price:true|frame-shape:partial|color:true|face-shape:false|fit:false|materials:false|lens-treatment:false; sgh-desktop-facet-state-search=; mt.v=2.226799281.1634257372609; bm_sv=B90661DFD942A0431D1A974DF69E74B2~GMqwfB7I0hw08srWCzoOZiiJS8cO3n69nAPvBTDerDbVPbd4Jwk3XJCN40IRXA9Oi8XSPi4QorP7o4daGeL7BoMgoCHIWsyeQfQl+rttCp1rlOAJe/5Y5DNwr5DAcgt7vBoJblP4vk/Rp3VFP8cXElkHYgQPvNvbA9r+/ybhk0Q=; utag_main=v_id:017c8154886c000e8b2adc3d241f0004c0039009009dc$_sn:1$_se:10$_ss:0$_st:1634259607848$ses_id:1634257373293%3Bexp-session$_pn:4%3Bexp-session$vapi_domain:sunglasshut.com$dc_visit:1$dc_event:3%3Bexp-session$dc_region:eu-central-1%3Bexp-session; tealium_data_session_timeStamp=1634257373355; userToken=undefined; TrafficSource_Override=1; AMCV_125138B3527845350A490D4C%40AdobeOrg=-1303530583%7CMCIDTS%7C18916%7CMCMID%7C05787876780449747262418047158326800711%7CMCAAMLH-1634862173%7C6%7CMCAAMB-1634862173%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1634264573s%7CNONE%7CMCAID%7CNONE%7CMCSYNCSOP%7C411-18923%7CvVersion%7C3.3.0; AMCVS_125138B3527845350A490D4C%40AdobeOrg=1; s_ecid=MCMID%7C05787876780449747262418047158326800711; _cs_mk=0.2828239252964845_1634257377428; s_cc=true; WC_AUTHENTICATION_1453854362=1453854362%2CkQ1pBK6BeZ5UdgafvUWkMz%2FWcCYravOxGOgMNz%2BPCIQ%3D; WC_USERACTIVITY_1453854362=1453854362%2C14351%2Cnull%2Cnull%2C1634257383842%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C1892784604%2C7uxdYgXLJ2YvbxIJAicjo7U2SovBjVDk3wrAU4hQf9rZJi14jvf8fs9lnTLCm1sBTQkwmEvy%2F6U9keNXwR1kPk3Ti6zwFKLSmmXMR8jBuvAm2BnSn8Nwd%2FeRUBzWcDXQlG%2F2XZjqbHAwffgZGO02L3PqpYa66W%2F1SJ8P4W6sfQuJbQaHfy7nYWuQYMXAI933xhmGVNiGj0S9kbOKXgbJDlkxhrGdyDF%2FBlJz2oiPKw0woSCYCfdqx2Q8rz8aTlEsoCjtxLtq9XR5ONfo7OWoNA%3D%3D; CONSENTMGR=consent:true%7Cts:1634257582458; _gcl_au=1.1.2104666974.1634257386; _scid=ebf30828-6da3-4702-9104-0b7ced89f23f; __utma=110589831.262718165.1634257387.1634257387.1634257387.1; __utmb=110589831.4.10.1634257387; __utmc=110589831; __utmz=110589831.1634257387.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1; _sctr=1|1634245200000; rxVisitor=1634257370850F4MBOT25O648EQB1C6ER8OI37ICU8648; dtSa=-; WC_AUTHENTICATION_-1002=-1002%2C5mduE4auFesN87pDyNccBg3A3LZom4jI7UYlAbvrvHg%3D; WC_USERACTIVITY_-1002=-1002%2C13801%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C1892784604%2CvkiKS6jf5KM%2FDK8rmKGGIEWI5RZiLH%2B32rISEt8kqno%2Ffdw80ARQ6yqgUKA98TwT%2FrE%2FKotSzV%2FbIjdv0u%2B5DZPdWMh5%2FI9DB4RqtJZTujcvPX%2BolXTrDuI9CzG6jkFV%2FnhmcCVKoGrwz%2B2VZ9BzdJL%2Frfcpf5afzxnG3Bo9cneaw8swGvsBxM8sPt9S1acDR34dXq%2Bqu07fdgMfpufKacQr6rZRzD%2B%2BXNkByJd%2F2zhq3%2BRxQODF0G51IPzA%2B%2B2f; WC_GENERIC_ACTIVITYDATA=[10097989472%3Atrue%3Afalse%3A0%3AwFFyxFNittOPbGgqK7qGDvod82%2FeRXhTv5j9zvU6t8Q%3D][com.ibm.commerce.context.ExternalCartContext|null][com.ibm.commerce.context.entitlement.EntitlementContext|4000000000000004002%264000000000000004002%26null%26-2000%26null%26null%26null][com.ibm.commerce.store.facade.server.context.StoreGeoCodeContext|null%26null%26null%26null%26null%26null][com.ibm.commerce.catalog.businesscontext.CatalogContext|20603%26null%26false%26false%26false][CTXSETNAME|Store][com.ibm.commerce.context.base.BaseContext|13801%26-1002%26-1002%26-1][com.ibm.commerce.context.audit.AuditContext|1634234155302-370087][com.ibm.commerce.context.experiment.ExperimentContext|null][com.sgh.commerce.findinstore.context.FindInStoreDefaultStoreContext|null][com.ibm.commerce.giftcenter.context.GiftCenterContext|null%26null%26null][com.ibm.commerce.context.globalization.GlobalizationContext|-2%26EUR%26-2%26EUR]",
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
    locator_domain = "https://www.sunglasshut.com/fr"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
