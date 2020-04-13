import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
import requests
import time
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addressesess = []
    url = "https://www.adventhealth.com/views/ajax?_wrapper_format=drupal_ajax"
    for data in range(0,51):
        querystring = {"_wrapper_format":"drupal_ajax"}
        payload = "view_name=ahs_facility_search_list&view_display_id=map&view_dom_id=b0da30de68d9f6634a06d1872be164a69563df4a3477c2c70378c9bbd380baf4&pager_element=0&geolocation_geocoder_google_geocoding_api_state=1&page="+str(data)+"&_drupal_ajax=1&ajax_page_state%5Btheme%5D=ahs_theme&ajax_page_state%5Blibraries%5D=ahs_admin%2Fahstabletools%2Cahs_banners%2Femergency%2Cahs_breadcrumbs%2Fviews%2Cahs_datalayer%2Fvisitor_geolocation%2Cahs_js%2Fahs_tooltip%2Cahs_js%2Fanchor_links%2Cahs_js%2Fautocomplete%2Cahs_js%2Fform_validate.extended%2Cahs_js%2FiframeRedirector%2Cahs_js%2Frandom_hero_picker%2Cahs_media%2Fblazy_slick%2Cahs_microsites%2Fnon_microsite_page%2Cahs_search%2Fclear_all_facets_block%2Cahs_search%2Ffacet_facility_checkbox_widget%2Cahs_search%2Ffacets%2Cahs_search%2Ffacets_header_block%2Cahs_search%2Ffacets_module_checkbox_widget_extended%2Cahs_search%2Fgeolocation.links%2Cahs_search%2Fphysician_search.autocomplete%2Cahs_theme%2Fcore%2Cahs_views%2Fbef_auto_submit%2Cahs_views%2Fexposed_form_persistent_facets%2Cahs_views%2Fexposed_form_persistent_facets_ajax%2Cbetter_exposed_filters%2Fgeneral%2Ccore%2Fhtml5shiv%2Ccore%2Fpicturefill%2Cdatalayer%2Fhelper%2Cextlink%2Fdrupal.extlink%2Cfacets%2Fdrupal.facets.hierarchical%2Cgeolocation%2Fgeolocation.views.filter.geocoder%2Cparagraphs%2Fdrupal.paragraphs.unpublished%2Csearch_api_autocomplete%2Fsearch_api_autocomplete%2Csystem%2Fbase%2Cviews%2Fviews.module"
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
            'postman-token': "67ad5f12-df8c-ff6c-91cc-8ca13af8abd5"
        }
        try:
            response = requests.post(url, data=payload, headers=headers, params=querystring)
            json_data = json.loads(response.text)
        except:
            pass
        for data1 in json_data:
            if "data" in data1:
                soup = BeautifulSoup(data1['data'],'lxml')
                Address = soup.find_all("span",{"property":"streetAddress"})
                city1 = soup.find_all("span",{"property":"addressLocality"})
                state1 = soup.find_all("span",{"property":"addressRegion"})
                zip2 = soup.find_all("span",{"property":"postalCode"})
                phone1 = soup.find_all("a",{"class":"telephone"})
                link = soup.find_all("a",{"class":"button--blue--dark"})
                for index,data2 in enumerate(soup.find_all("a",{"class":"location-block__name-link u-text--fw-300 notranslate"})):
                    name = (data2.text)
                    street_address = Address[index].text.strip()
                    city = city1[index].text
                    state = state1[index].text
                    zip1 = zip2[index].text
                    try:
                        phone = phone1[index].text.split('at')[-1]
                    except:
                        phone = "<MISSING>"
                    page_url = link[index]['href']
                    hours2 ='<MISSING>'
                    page_url1='<MISSING>'
                    location_type ='<MISSING>'
                    latitude ='<MISSING>'
                    longitude ='<MISSING>'
                    if page_url:
                        try:
                            page_url1 = "https://www.adventhealth.com"+page_url.replace("https://www.adventhealth.com",'')
                        
                            response1 = requests.get(page_url1)
                        except:
                            pass

                        soup1 = BeautifulSoup(response1.text,'lxml')
                        try:
                            if "3A121"==soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1]:
                                location_type="Hospital and Emergency Rooms"
                            if "3A738"==soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1]:
                                location_type="Urgent Care"
                            if "3A123"==soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1]:
                                location_type="Institutes"
                            if "3A122" == soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1]:
                                location_type="Imaging"
                            if "3A124"==soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1]:
                                location_type ='Lab'
                            if "3A144"== soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1]:
                                location_type ='Home Care'
                            if "3A145"==soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1]:
                                location_type ='Hospice Care'
                            if "3A150"==soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1]:
                                location_type ='Skilled Nursing'
                            if "3A147"==soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1]:
                                location_type ='Pharmacy'
                            if "3A394"==soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1]:
                                location_type ='Wellness Centers'
                            if "3A397"==soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1]:
                                location_type ='Rehabilitation Service'
                            if "3A127"==soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1]:
                                location_type ='Surgery Centers'
                            if "3A398"==soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1]:
                                location_type ='Endoscopy Centers'
                            if "3A373"==soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1]:
                                location_type ="Practices"
                        except:
                            location_type="<MISSING>"

                        try:
                            latitude = soup1.find("meta",{"property":"latitude"})['content']
                            longitude = soup1.find("meta",{"property":"longitude"})['content']
                        except:
                            latitude='<MISSING>'
                            longitude = '<MISSING>'
                        hours1 = soup1.find("ul",{"class":"location-block__details-list"})
                        if  hours1 != None:
                            hours  = hours1.find("li").text.strip()

                        if "Visiting Hours:" in hours and "Visiting Hours: As we monitor coronavirus (COVID-19) in our communities, we have made changes to our visitation policies to ensure the safety of our patients, visitors and team members. Read our new visitation policy." != hours:
                            hours2 = hours.split("Emergency Care:")[0].replace("Visiting",'')

                    else:
                        page_url1 = "<MISSING>"
                        location_type = "<MISSING>"
                    if "AdventHealth has a responsibility" in hours2:
                        hours2 = "<MISSING>"
                    store = []
                    store.append("https://www.adventhealth.com")
                    store.append(name)
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
                    # print("data == "+str(store))
                    # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
