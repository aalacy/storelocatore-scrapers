const Apify = require('apify');
const axios = require('axios');
const domain = 'centracare.org';
const url = 'https://centracare-scheduling.adventhealth.io/ccrest/api/smartappts/locsall';

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {
  return await axios({method: "GET", url: url}).then((resp) => {
    returnData = [];  
    for (let entry of resp.data.CC_getlocs){returnData.push(mapData(entry));}
    return returnData;
  }).catch((e) => {handleError(e);})
}

function mapData(e){
  return {
    locator_domain: domain,
    location_name: e.location_name,
    street_address: e.address_line_1 + e.address_line_2,
    city: e.city,
    state: e.state,
    zip: e.zip,
    country_code: "US",
    store_number: e.locid,
    phone: e.phone,
    location_type: '<MISSING>',
    latitude: e.lat,
    longitude: e.lng,
    hours_of_operation: buildHours(e)
  }
}

function buildHours(e){
  ret = "";
  ret = ret + `Sunday ${e.open_sun} - ${e.close_sun}`
  ret = ret + `Monday ${e.open_mon} - ${e.close_mon}`
  ret = ret + `Tuesday ${e.open_tue} - ${e.close_tue}`
  ret = ret + `Wednesday ${e.open_wed} - ${e.close_wed}`
  ret = ret + `Thursday ${e.open_thu} - ${e.close_thu}`
  ret = ret + `Friday ${e.open_fri} - ${e.close_fri}`
  ret = ret + `Saturday ${e.open_sat} - ${e.close_sat}`
  return ret;
}


function handleError(e){
  console.error("Error retrieving centracare.org locations: ", e);
}