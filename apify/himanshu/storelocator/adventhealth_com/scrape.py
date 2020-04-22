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
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []
    base_url = locator_domain = "https://www.adventhealth.com"
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = "<MISSING>"
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    raw_address = ""
    page_url = ""
    hours_of_operation = ""
    
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
            response = requests.post(url, data=payload, headers=headers, params=querystring)
            json_data = json.loads(response.text)
        except:
            pass
        for data1 in json_data:
            if "data" in data1:
                if "No locations were found that match your search" in data1['data']:
                    break
                soup = BeautifulSoup(data1['data'],'lxml')
                # print(soup.prettify())
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                for li in soup.find_all("li",class_="facility-search-block__item"):
                    try:
                        location_name = li.find("div",class_="location-block__headline").find("a").text.strip()
                    except:
                        location_name = "<MISSING>"
                    # page_url = "https://www.adventhealth.com"+li.find("div",class_="location-block__headline").find("a")["href"]
                    street_address = li.find("span",{"property":"streetAddress"}).text.strip()
                    try:
                        city = li.find("span",{"property":"addressLocality"}).text.strip()
                    except:
                        city = "<MISSING>"
                    try:
                        state = li.find("span",{"property":"addressRegion"}).text.strip()
                    except:
                        state = "<MISSING>"
                    try:
                        zipp = li.find("span",{"property":"postalCode"}).text.strip()
                    except:
                        zipp = "<MISSING>"
                    country_code= "US"
                    try:
                        phone_tag = li.find("span",{"class":"location-block__telephone-text"})
                        phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_tag))
                        if phone_list:
                            phone = phone_list[0]
                        else:
                            phone = "<MISSING>"
                    except:
                        phone ="<MISSING>"
                    try:
                        page_url = li.find("a",class_="button--blue--dark")["href"]
                        if page_url:
                            try:
                                if "http" in page_url:
                                    page_url1 = page_url
                                else:
                                    page_url1 = "https://www.adventhealth.com"+page_url
                                # print(page_url1)
                                response1 = requests.get(page_url1)
                            except:
                                pass

                            soup1 = BeautifulSoup(response1.text,'lxml')
                            try:
                                if "3A121"==soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1] or "hospital" in page_url1:
                                    location_type="Hospital and Emergency Rooms"
                                if "3A738"==soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1] or "urgent-care" in page_url1:
                                    location_type="Urgent Care"
                                if "3A123"==soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1] or "institites" in page_url1:
                                    location_type="Institutes"
                                if "3A122" == soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1] or "imaging" in page_url1:
                                    location_type="Imaging"
                                if "3A124"==soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1] or "lab" in page_url1:
                                    location_type ='Lab'
                                if "3A144"== soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1] or "home-care" in page_url1:
                                    location_type ='Home Care'
                                if "3A145"==soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1] or "hospice-care" in page_url1:
                                    location_type ='Hospice Care'
                                if "3A150"==soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1] or "skilled-nursing" in page_url1:
                                    location_type ='Skilled Nursing'
                                if "3A147"==soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1] or "pharmacy" in page_url1:
                                    location_type ='Pharmacy'
                                if "3A394"==soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1] or "wellness-centers" in page_url1:
                                    location_type ='Wellness Centers'
                                if "3A397"==soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1] or "rehabilitation-service" in page_url1:
                                    location_type ='Rehabilitation Service'
                                if "3A127"==soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1] or "surgery-centers" in page_url1:
                                    location_type ='Surgery Centers'
                                if "3A398"==soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1] or "endoscopy-centers" in page_url1:
                                    location_type ='Endoscopy Centers'
                                if "3A373"==soup1.find("a",{"class":"location-bar__change"})['href'].split("facility_type%")[-1] or "practices" in page_url1:
                                    location_type ="Practices"
                            except:
                                location_type="<MISSING>"
                            try:
                                latitude = soup1.find("meta",{"property":"latitude"})['content']
                                longitude = soup1.find("meta",{"property":"longitude"})['content']
                            except:
                                latitude='<MISSING>'
                                longitude = '<MISSING>'
                            try:
                                hours_of_operation =" ".join(list(soup1.find("ul",{"class":"location-block__details-list"}).stripped_strings)).replace(" Our urgent care center in Apopka accepts most major insurance plans. Click here to see a list of the insurance plans we accept.","").strip()
                            except:
                                hours_of_operation = "<MISSING>"
                            if "Visiting Hours" in hours_of_operation and "Visiting Hours: As we monitor coronavirus (COVID-19) in our communities, we have made changes to our visitation policies to ensure the safety of our patients, visitors and team members. Read our new visitation policy." != hours_of_operation:
                                hours_of_operation = hours_of_operation.split("Emergency Care:")[0].replace("Visiting",'')
                            if "AdventHealth has a responsibility" in hours_of_operation:
                                hours_of_operation = "<MISSING>"

                            hours_of_operation = hours_of_operation.replace("Visiting Hours: As we monitorcoronavirus (COVID-19) in our communities, we have made changes to our visitation policies to ensure the safety of our patients, visitors and team members. Read our new visitation policy.","").replace("Care Close to Home: Located at K-7 and Prairie Star Parkway in western Lenexa, this comprehensive health care facility can be easily accessed from K-7, K-10, I-435 and I-35  allowing area residents to receive care from the most talented and skillful health care professionals in the region.","").replace(" Amenities: Eden Spa Outdoor healing garden Calming and comforting chapel Pastoral care Two Pharmacy Locations Three Market Place Gift Shops AdventHealth Wellness Center Orlando","").replace("Call Call 813-715-6618 to connect with a chaplain","")
                    except:
                        page_url1 = "<MISSING>"
                        location_type = "<MISSING>"
                        latitude = "<MISSING>"
                        longitude = "<MISSING>"
                        hours_of_operation= "<MISSING>"
                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                    store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url1]
                    store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]


                    if (str(store[2])+str(store[-1])) in addresses:
                        continue
                    addresses.append(str(store[2])+str(store[-1]))

                    #print("data = " + str(store))
                    #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    
                    yield store    
                    
        page+=1
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
