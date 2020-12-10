import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
import time
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addressesess = []
    url = "https://www.adventhealth.com/views/ajax?_wrapper_format=drupal_ajax"
    page = 0
    while True:
        querystring = {"_wrapper_format":"drupal_ajax"}
        payload = "view_name=ahs_facility_search_list&view_display_id=map&view_dom_id=b0da30de68d9f6634a06d1872be164a69563df4a3477c2c70378c9bbd380baf4&pager_element=0&geolocation_geocoder_google_geocoding_api_state=1&page="+str(page)+"&_drupal_ajax=1&ajax_page_state%5Btheme%5D=ahs_theme&ajax_page_state%5Blibraries%5D=ahs_admin%2Fahstabletools%2Cahs_banners%2Femergency%2Cahs_breadcrumbs%2Fviews%2Cahs_datalayer%2Fvisitor_geolocation%2Cahs_js%2Fahs_tooltip%2Cahs_js%2Fanchor_links%2Cahs_js%2Fautocomplete%2Cahs_js%2Fform_validate.extended%2Cahs_js%2FiframeRedirector%2Cahs_js%2Frandom_hero_picker%2Cahs_media%2Fblazy_slick%2Cahs_microsites%2Fnon_microsite_page%2Cahs_search%2Fclear_all_facets_block%2Cahs_search%2Ffacet_facility_checkbox_widget%2Cahs_search%2Ffacets%2Cahs_search%2Ffacets_header_block%2Cahs_search%2Ffacets_module_checkbox_widget_extended%2Cahs_search%2Fgeolocation.links%2Cahs_search%2Fphysician_search.autocomplete%2Cahs_theme%2Fcore%2Cahs_views%2Fbef_auto_submit%2Cahs_views%2Fexposed_form_persistent_facets%2Cahs_views%2Fexposed_form_persistent_facets_ajax%2Cbetter_exposed_filters%2Fgeneral%2Ccore%2Fhtml5shiv%2Ccore%2Fpicturefill%2Cdatalayer%2Fhelper%2Cextlink%2Fdrupal.extlink%2Cfacets%2Fdrupal.facets.hierarchical%2Cgeolocation%2Fgeolocation.views.filter.geocoder%2Cparagraphs%2Fdrupal.paragraphs.unpublished%2Csearch_api_autocomplete%2Fsearch_api_autocomplete%2Csystem%2Fbase%2Cviews%2Fviews.module"
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
            'postman-token': "67ad5f12-df8c-ff6c-91cc-8ca13af8abd5"
        }
        try:
            response = session.post(url, data=payload, headers=headers, params=querystring)
            json_data = json.loads(response.text)
        except:
            continue
        soup = BeautifulSoup(json_data[-1]['data'],"lxml")
        if "No locations were found that match your search" in soup.text:
            break
        
        loc_type = {"3A121":"Hospital and Emergency Rooms","3A738":"Urgent Care","3A123":"Institutes","3A122":"Imaging","3A124":"Lab","3A144":"Home Care","3A145":"Hospice Care","3A150":"Skilled Nursing","3A147":"Pharmacy","3A394":"Wellness Centers","3A397":"Rehabilitation Service","3A127":"Surgery Centers","3A398":"Endoscopy Centers","3A373":"Practices"}

        for info  in soup.find_all("li",{"class":"facility-search-block__item"}):
            try:
                if "Coming Soon" == info.find("p",{"class":"location-block__endorsement"}).text.strip():
                   
                    continue
            except:
                pass
            try:
                location_name = info.find("a",{"class":"location-block__name-link u-text--fw-300 notranslate"}).text.strip()
            except:
                location_name = info.find("h3",{"class":"location-block__name"}).text.strip()
            street_address = info.find("span",{"property":"streetAddress"}).text.strip().split("Suite")[0].replace(",","").replace("3rd Floor","").replace("1st Floor","").replace("8th Floor","").replace("3rd floor","").replace("2nd Floor","").replace("Floor 2","").strip()
             
            city = info.find("span",{"property":"addressLocality"}).text.strip()
            try:
                state = info.find("span",{"property":"addressRegion"}).text.strip()
            except:
                state = "<MISSING>"
            zip1 = info.find("span",{"property":"postalCode"}).text.strip()
            try:
                phone = info.find("a",{"class":"telephone"}).text.split('at')[-1]
                
            except:
                phone = "<MISSING>"
            
            try:
                page_url = info.find("a",{"class":"button--blue--dark"})['href']
               
                hours2 =''
                if page_url:
                    if "http" in page_url:
                        page_url1 = page_url
                    else:
                        page_url1 = "https://www.adventhealth.com"+page_url
                    response1 = session.get(page_url1)
                    soup1 = BeautifulSoup(response1.text,'lxml')
                    try:
                        location_type = loc_type[soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1]]
                    except:
                        location_type="<MISSING>"

                    try:
                        latitude = soup1.find("meta",{"property":"latitude"})['content']
                        longitude = soup1.find("meta",{"property":"longitude"})['content']
                    except:
                        latitude='<MISSING>'
                        longitude = '<MISSING>'
                    try:
                        hours1 = soup1.find("ul",{"class":"location-block__details-list"})
                        if  hours1 != None:
                            hours  = hours1.find("li").text.strip()

                        if "Visiting Hours" in hours and "Visiting Hours: As we monitor coronavirus (COVID-19) in our communities, we have made changes to our visitation policies to ensure the safety of our patients, visitors and team members. Read our new visitation policy." != hours:
                            hours2 = hours.split("Emergency Care:")[0].replace("Visiting",'')
                           
                    except:
                       
                        hours2 = " ".join(list(soup1.find("div",{"class":"location-information-widget__top-right"}).stripped_strings))
                       

                else:
                    page_url1 = "<MISSING>"
                    hours2 ='<MISSING>'
                    location_type ='<MISSING>'
                    latitude ='<MISSING>'
                    longitude ='<MISSING>'
            except:
                page_url1 = "<MISSING>"
                hours2 ='<MISSING>'
                location_type ='<MISSING>'
                latitude ='<MISSING>'
                longitude ='<MISSING>'
            store = []
            store.append("https://www.adventhealth.com")
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zip1 if zip1 else "<MISSING>")
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append(location_type if location_type else "<MISSING>")

            store.append(latitude)
            store.append(longitude)
            hours2 = hours2.replace(" secondary shift change (secondary to patient information being exchanged between the nurses and the providers) and only 2 visitors at a bedside.",'')
            store.append(hours2.replace("\n",' ').replace("Hours:  Hours:",'Hours:').replace(",",' ') if hours2 else "<MISSING>")
            store.append(page_url1 )
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            if store[2] in addressesess:
                continue
            addressesess.append(store[2])
           
            yield store
        page+=1
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
