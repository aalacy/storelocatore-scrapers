from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://www.sunglasshut.com/AjaxSGHFindPhysicalStoreLocations?latitude={}&longitude={}&radius=200"
    domain = "sunglasshut.com/es"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,ru-RU;q=0.8,ru;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Cookie": "JSESSIONID=0000t2AwRlOEZ8eOPh2shPd_J6v:1c7qtqjbr; WC_PERSISTENT=SiAUE8UVI8osRRnypG%2B0KxLmJkM5vWk0OP0M63s2QsI%3D%3B2021-10-14+11%3A45%3A29.719_1634211929715-371697_13251_-1002%2C-5%2CEUR_13251; metroCode=0; COUNTRY=HK; CATALOG_ASSORTMENT=SGH; WC_SESSION_ESTABLISHED=true; WC_AUTHENTICATION_-1002=-1002%2C5mduE4auFesN87pDyNccBg3A3LZom4jI7UYlAbvrvHg%3D; WC_ACTIVEPOINTER=-5%2C13251; WC_USERACTIVITY_-1002=-1002%2C13251%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C1665284906%2CTF%2FmzJ79sQ5AI%2B3P3BsKPcrA%2FsA5IQXh11EqqnjZDqHdHKgPsowXVtuIFT0bVFgEXLMALbYD9QsJm%2FctdvTJDmgTxbYOLyR6MXlm3ocdpYlbjRPJEg8qokBfk0zEKWabNiKr4LEgfIsQaZEViRVc59i5QOOb1ObzTHtsQIhR2yWXADkabtHGU8VCT1PLJeN94NMXIc5eRhMKvRkqPsiVU57U96wXMOw07Rqc8glCbfdHJVLm6xOdZzU5Omyrs3LC; WC_GENERIC_ACTIVITYDATA=[10096095741%3Atrue%3Afalse%3A0%3AW8bobaUFtjwvfPrJ5YclHXdeJXFUB%2FQBB6G2iSiP13o%3D][com.ibm.commerce.context.ExternalCartContext|null][com.ibm.commerce.context.entitlement.EntitlementContext|4000000000000003502%264000000000000003502%26null%26-2000%26null%26null%26null][com.ibm.commerce.store.facade.server.context.StoreGeoCodeContext|null%26null%26null%26null%26null%26null][com.ibm.commerce.catalog.businesscontext.CatalogContext|20603%26null%26false%26false%26false][CTXSETNAME|Store][com.ibm.commerce.context.base.BaseContext|13251%26-1002%26-1002%26-1][com.ibm.commerce.context.audit.AuditContext|1634211929715-371697][com.ibm.commerce.context.experiment.ExperimentContext|null][com.sgh.commerce.findinstore.context.FindInStoreDefaultStoreContext|null][com.ibm.commerce.giftcenter.context.GiftCenterContext|null%26null%26null][com.ibm.commerce.context.globalization.GlobalizationContext|-5%26EUR%26-5%26EUR]; TS011f624f=015966d292dcdce666df23eb6a61dc45ed77a2f4109898693f54f8b7468742f15e7c8ddad63175ea6fb03cceda3ab5b70ed215e64e645873b286352ea1e6f278bb167a8d44a0fc7fbda0a62802dcdb859a8fb049760b3a392cdac7f930ac467cf0202cdd00b0137eff286b6998ce0ca469de0cf8ba34375a6a7690d3556f0c53b1bc5cf8e54de00a26c5387f50595dc331ba6206cf8f2d5203fa07abc9dc8d23facaa30e7ea8497bed2142b7807f255bd7884173a2a029ac753d7ff65ccc3be347a7dc311b4fee17d6fe2ef1be3169c62735d146c037b2e083dd25572ee2c13558ea780176; aka-cc=ES; aka-ct=MADRID; aka-zp=; ak_bmsc=1DABF1F251EFB5A5ED592C6E6AFDEF25~000000000000000000000000000000~YAAQXycRAgoxAXl8AQAAojaffg1Skz+nU/VGUeCGTwpBvqu3bEIcfmewuqxUgjDC9OPcFEZLp6ifDXMlrP1AHbgAyIt5aMBwP66OSDOQMzGypoQBy9wu2m31k+II+bWHvISe/CxC/41abkvWpG5EqDcoCMkh+6aqwd/k9oB7CBYRIM5ZrRWBYfwKp/qzAF+peZd7upWk86HMFFKHrpyekTcg6OiRfeISe4nsIxcJ8n/tKfPFVxR7JbmAfPe7jF0HnHNfQBJjzeJtQHV42Iamjqqrkl8eHbvyx9zQJsaH/TtJ+8ubPkPnau3tR5LyhCSid0vOLMIr8mxNLd9ipyiz4xLbIMef1MxUJq0X8iMGee7HeMVcQJqz9aatyjCP7s0nDKdaSweJwzPxfSPQlHuOWIGcktRuZwtoL+sbPydijuvDMoC8ExCeNATdPhor+4iw46tUIQh3QxHzlK9Oi4ZnPmHOiWvkLusjfeQcy0V37EXLua4JfLxXz0N7M6AOyV77iD4x0imHTGdNwwVaCXjLVfi1Le47WdvQ6g==; SGPF=3B8o3cxU_dhqnD8S0Xertgw6-GQAVrfkg6p1lE4wlhefrT_m2gQNZEQ; forterToken=b62cfed74f08415a93f7554e6c3284a1_1634211958767__UDF43_6; dtCookie=v_4_srv_2_sn_J2VP0LUILDN4UBK2N1HPK12GCERNDA3T_app-3Ab359c07662f0b428_0_ol_0_perc_100000_mul_1; rxVisitor=1634211932530CG0MIRO887H9GS1QFRKLG9TDHRMVRMJ1; dtPC=2$411957813_780h1vSKTFAAFSHOALMEHPIRJRFQKHHHBRMKDI-0e1; rxvt=1634213737542|1634211932532; dtSa=-; dtLatC=106; sgh-desktop-facet-state-plp=categoryid:undefined|gender:true|brands:partial|polarized:true|price:true|frame-shape:partial|color:true|face-shape:false|fit:false|materials:false|lens-treatment:false; sgh-desktop-facet-state-search=; utag_main=v_id:017c7e9f3485004a7991916f2a1800052003900f00838$_sn:1$_se:7$_ss:0$_st:1634213759271$ses_id:1634211935366%3Bexp-session$_pn:2%3Bexp-session$vapi_domain:sunglasshut.com$dc_visit:1$dc_event:1%3Bexp-session$dc_region:eu-central-1%3Bexp-session; tealium_data_session_timeStamp=1634211935418; bm_sv=90F70FBCF203C11F2C0ECE7EEDDE8289~CJjCmd6WxtzYbpPO2V4LEbA2G0RDicF2fGPWKMN+abjIhUb0uf/1B0qIFcHBui5ZM4jXa604esKEmJmRcjM1w0S12EOAgason/N6MmqNqTFw8A2Xu3uWMpP3Y6Xev5+vhh0lq4PPXNIl32XKnFJi02asVW/AVk1jqODkEZQAKuk=; userToken=undefined; TrafficSource_Override=1; AMCV_125138B3527845350A490D4C%40AdobeOrg=-1303530583%7CMCIDTS%7C18915%7CMCMID%7C37154648669072542591651943396872180891%7CMCAAMLH-1634816736%7C9%7CMCAAMB-1634816736%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1634219136s%7CNONE%7CMCSYNCSOP%7C411-18922%7CMCAID%7CNONE%7CvVersion%7C3.3.0; mt.v=2.1070531774.1634211935915; ftr_ncd=6; __wid=562155275; AMCVS_125138B3527845350A490D4C%40AdobeOrg=1; CONSENTMGR=consent:true%7Cts:1634211939030; s_ecid=MCMID%7C37154648669072542591651943396872180891; _gcl_au=1.1.2144750046.1634211940; _scid=f0b35c0a-5a69-4c65-971a-98af2eb8a726; __utma=110589831.161057800.1634211941.1634211941.1634211941.1; __utmb=110589831.2.9.1634211941; __utmc=110589831; __utmz=110589831.1634211941.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1; _fbp=fb.1.1634211941551.302339796; rxVisitor=1634211932530CG0MIRO887H9GS1QFRKLG9TDHRMVRMJ1; cto_bundle=Hl6JXl9zYnpVc0xndE84SnFFcFZPeGZYdjZ2JTJGUEk2UGoyNG9FNk9IOFlUWVRZWUljU3huakxWWnQwRVM0TlJ6VmhEUjNEYm1TUWVkYktncHZ2bjZ6cG5qUjB5dFMwZG1TVU9aJTJGd000cnFNcGwlMkZITEpxdnVQNVROcGdlSUNJejc2VHdNS2p3QWs5WUlOclplclFNeGpUVWZKbFBPcFB2NWNNVElaREZwOTJTSklHRGF0OE9HS2ZaR2lNNjlRN3hVWWtaRTV3WWhNM1p4cCUyRlpuTW42aXF3NGtwbHclM0QlM0Q; dtSa=true%7CKU13%7C-1%7CIntroduce%20una%20ubicaci%C3%B3n%20%28c%C3%B3digo%20postal%5Ec%20direcci%C3%B3n%20o%20ciudad%29%7C-%7C1634211954503%7C411932527_907%7Chttps%3A%2F%2Fwww.sunglasshut.com%2Fes%2Fsunglasses%2Fstore-locations%7CStore%20Locator%7C1634211938864%7C%7C",
    }
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.SPAIN], expected_search_radius_miles=200
    )
    for lat, lng in all_coords:
        data = session.get(start_url.format(lat, lng), headers=hdr).json()
        all_locations = data["locationDetails"]
        for poi in all_locations:
            hoo = []
            for e in poi["hours"]:
                hoo.append(f'{e["day"]} {e["open"]} - {e["close"]}')
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.sunglasshut.com/es/sunglasses/store-locations",
                location_name=poi["displayAddress"],
                street_address=poi["shippingDetails"]["street"],
                city=poi["shippingDetails"]["city"],
                state="",
                zip_postal=poi["shippingDetails"]["zipCode"],
                country_code=poi["shippingDetails"]["country"],
                store_number=poi["id"],
                phone=poi["phone"],
                location_type=poi["storeType"],
                latitude=poi["latitude"],
                longitude=poi["longitude"],
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
