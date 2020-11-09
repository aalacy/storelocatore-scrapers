from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
import sgzip
from sgzip import SearchableCountries

def fetch_data():
    url = "https://www.pearlevision.com/webapp/wcs/stores/servlet/AjaxStoreLocatorResultsView?resultSize=5000&latitude="
    headers = {
'Host': 'www.pearlevision.com',
'Connection': 'keep-alive',
'Cache-Control': 'max-age=0',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'Sec-Fetch-Site': 'none',
'Sec-Fetch-Mode': 'navigate',
'Sec-Fetch-User': '?1',
'Sec-Fetch-Dest': 'document',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'en-US,en;q=0.9,ro;q=0.8',
'Cookie': str(''.join([#'CONSENTMGR=consent:true;',
           #'AMCVS_125138B3527845350A490D4C%40AdobeOrg=1;',
           #'s_ecid=MCMID%7C57863718548565117832917647147770505463;',
           #'s_cc=true;',
           #'_gcl_au=1.1.537451646.1604765255;',
           #'WC_SESSION_ESTABLISHED=true;',
           #'WC_PERSISTENT=FuRG%2BXqQLjxhaFi0hUDD3QKQ9mQtEZwjdNLZIoSS6fE%3D%3B2020-11-07+16%3A08%3A02.225_1604765260114-168850_12002_-1002%2C-1%2CUSD%2C2020-11-07+16%3A08%3A02.225_12002;',
           'WC_AUTHENTICATION_-1002=-1002%2CCgQ64D1HPFU01Yzxj60dChBZ%2BEti%2B5IrxEDLfbZmZ4s%3D;',
           'WC_ACTIVEPOINTER=-1%2C12002;',
           'WC_USERACTIVITY_-1002=-1002%2C12002%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C1026820673%2CupR%2F4d1swhtdePOXYAL14xfJz2FMjxPwIivkT1LpqHUmxYQ1NyGn7OPm4il0%2BlkqR6s6P50fCyTr1yUvRoOQo%2BcAzmwGRtW9GJkB%2BNGHO%2BnAX6SpC7xmi7jt2NDP3A0a0sCQHWgNgtQIaWBrKt1VFxEhIDnavGFpRYfo8k6XyjrlG1qjwutW34keK6DY0De0imDFIkHJar9DCzZy%2BWev9NSuO%2BaM0b1BlpjaGMklTyhaLVs8C1twGN1DwPo3uQnw;',
           'WC_GENERIC_ACTIVITYDATA=[7703325384%3Atrue%3Afalse%3A0%3AsQ6BPvrKRCa%2FPm5rt4ZdE1AJRXht7u%2FSR5NmKPccIlg%3D][com.ibm.commerce.context.ExternalCartContext|null][com.ibm.commerce.context.entitlement.EntitlementContext|4000000000000001506%264000000000000001506%26null%26-2000%26null%26null%26null][com.ibm.commerce.store.facade.server.context.StoreGeoCodeContext|null%26null%26null%26null%26null%26null][com.ibm.commerce.catalog.businesscontext.CatalogContext|15951%26null%26false%26false%26false][CTXSETNAME|Store][com.ibm.commerce.context.base.BaseContext|12002%26-1002%26-1002%26-1][com.ibm.commerce.context.audit.AuditContext|1604765260114-168850][com.ibm.commerce.context.experiment.ExperimentContext|null][com.ibm.commerce.giftcenter.context.GiftCenterContext|null%26null%26null][com.ibm.commerce.context.globalization.GlobalizationContext|-1%26USD%26-1%26USD];',
           #'_ga=GA1.2.20649102.1604765920;',
           #'_gid=GA1.2.855605919.1604765920;',
           #'city=dallas;',
           #'state=tx;',
           #'zipcode=75227%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20;',
           #'country=United%20States;',
           #'JSESSIONID=0000MeTUZVr3G0_V40kjdeSejOM:1cm5l6v9o;',
           #'TS017a0b15=0198a40b24c11a28835af4ca84042425f32dab4f57bd5f9f0f10ec939877302a4f6e0a21d856ccf91ab5216ac119cb337445ab2eae0f512517ea5adbb713a469715ab41e3803415f437822d63d748aabcca3f855d71e01bd594530c30feb78d2db5f5e6468dd2c8baa04d2c1b4568291d2c54d1a6c85cec763e9f31ebfa8ed26516f011beaf9df6c8a9c7a4f9f2b1aee430416ce5bf03f155eed9c262d80b8fc068567e22a3fa27338510387f3384a9078a320f0ad;',
           #'ak_bmsc=65C8B22DB28D009DC3B036837BCC74570214F8AD6B5B000081EBA75FB2565F73~plLobeG2huAHH8aJpJ2bE0jOw8cTR2YcYO6vM4xpUk/79i4lTVXLEQHMMbnOIYdmS7D+y0Fvacw44mzvDTgk0rwJW2aV2cwPyQZaKBn4I1bqwZ+fIowPOc/uUtj0uQ7bVnjy8HtV8qu+A6QpESXbkShB49w/a9+do1II187fxrGsB/K0u6wPLaxAY70IGOgJU4l4Wa8LhGaemUzKxEYB0rKlxEXaF8lGfZ9kjXoiYVi+0lRHgJ1B262P4blsovCxPa;',
           #'AMCV_125138B3527845350A490D4C%40AdobeOrg=-1303530583%7CMCIDTS%7C18574%7CMCMID%7C57863718548565117832917647147770505463%7CMCAAMLH-1605445126%7C6%7CMCAAMB-1605445126%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1604847526s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C3.3.0;',
           #'utag_main=v_id:0175a37680d100170ef3bcc72cd503072001d06a0086e$_sn:2$_se:3$_ss:0$_st:1604842167602$vapi_domain:pearlevision.com$dc_visit:2$ses_id:1604840324885%3Bexp-session$_pn:3%3Bexp-session$dc_event:2%3Bexp-session$dc_region:eu-central-1%3Bexp-session;',
           #'_tq_id.TV-27631836-1.c5a8=94ebbf1cda2dfd44.1604765255.0.1604840369..;',
           #'s_sq=lux-pearle-prod%3D%2526c.%2526a.%2526activitymap.%2526page%253D%25252Fpv-us%25252Feye-care-center-locator%2526link%253DGO%2526region%253DStoreLocatorForm%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253D%25252Fpv-us%25252Feye-care-center-locator%2526pidt%253D1%2526oid%253DGO%2526oidt%253D3%2526ot%253DSUBMIT;',
           #'latitude=40.7127753;',
           #'longitude=-74.0059728;',
           #'lastValidStoreSearch=New%20York;',
           #'TS0167bc91=0198a40b240090be50cff74098e5d5891c3bc7b01b36878dacb811a0a5c21cf5d8cbc7cc7a950f6441ce1e9b18f30e77f1b38300f3eeda0defd3f02f33e54a1ec68f1acb3c0912eb9664c2b7c5e33d089f3589df2949e2089daec16434128f95a873b3ee50c1d24c9bbb448ed41f2bf9d363415719defc3dd597ee011fbbd0333cb7237638ecd594321c6481a6a927806f6c90921b6551f5c9baa617d9e9efa4191a841f90;',
           #'bm_sv=01D89CBF1203FFBC074EC19C1603D271~PGcOdTnAl5uciJyQC6DKHt4yKXr9YjuBkYh0q22MNrx2zwYHV6mo0hNlT4CnfthU2ztJXXM1BFROa1CFphOjJbiKm/ByJk1+BBddKIRPE4uRpsD4U5fJnLKHvLd32s9VHzD1MWhc+NfnNVKPmKoQkUXC0LMfqo0Xh3ICH+LgyTY='
           ]))
}
    coords = sgzip.coords_for_radius(radius=99, country_code=SearchableCountries.USA)
    
    j = utils.parallelize(
                search_space = coords,
                fetch_results_for_rec = lambda x : net_utils.fetch_xml(
                                                    root_node_name='body',
                                                    location_node_name='div',
                                                    location_node_properties={'class':'store-data'},
                                                    request_url="https://www.pearlevision.com/webapp/wcs/stores/servlet/AjaxStoreLocatorResultsView?resultSize=5000&latitude="+x[0]+"&longitude="+x[1],
                                                    headers=headers),
                max_threads = 15,
                print_stats_interval = 15)
    for i in j:
        for h in i:
            yield h


         
def scrape():
    url="https://www.pearlevision.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),#,
        page_url=MappingField(mapping=['span class=[website]','span class=[website]'], is_required = False),
        location_name=MappingField(mapping=['span class=[storeName]','span class=[storeName]']),
        latitude=MappingField(mapping=['span class=[latitude]','span class=[latitude]']),
        longitude=MappingField(mapping=['span class=[longitude]','span class=[longitude]']),
        street_address=MappingField(mapping=['span class=[address]','span class=[address]'], is_required = False),
        city=MappingField(mapping=['span class=[city]','span class=[city]']),
        state=MappingField(mapping=['span class=[state]','span class=[state]']),
        zipcode=MappingField(mapping=['span class=[zipCode]','span class=[zipCode]']),
        country_code=ConstantField("US"),#MappingField(mapping=[], ),
        phone=MappingField(mapping=['span class=[phone]','span class=[phone]'], part_of_record_identity = True),
        store_number=MappingField(mapping=['span class=[storeNumber]','span class=[storeNumber]'], part_of_record_identity = True),
        hours_of_operation=MappingField(mapping=['span class=[hours]','span class=[hours]']),
        location_type=MissingField()#MappingField(mapping=[], is_required = False)
    )

    pipeline = SimpleScraperPipeline(scraper_name='pearlevision.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=5)

    pipeline.run()

if __name__ == "__main__":
    scrape()
