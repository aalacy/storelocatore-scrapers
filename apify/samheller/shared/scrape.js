const Apify = require('apify');
const axios = require('axios');
const jsdom = require("jsdom");
const { JSDOM } = jsdom;

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape(){
  
}

async function pageList(){
  return await axios({
    method: "",
    url: ""
  }).then((resp) => {
    dom = getDom(resp.data);
    links = [];
    for (let l of dom.querySelectorAll('')){
        links.push({url: '' + l.getAttribute('href')})
    }
  })
}

function getDom(markup){
  dom = new JSDOM(markup);
  return dom.window.document;
}

function getRecord(domain = '<MISSING>'){
  return {
    locator_domain: domain,
    location_name: '<MISSING>',
    street_address: '<MISSING>',
    city: '<MISSING>',
    state: '<MISSING>',
    zip: '<MISSING',
    country_code: '<MISSING>',
    store_number: '<MISSING>',
    phone: '<MISSING>',
    location_type: '<MISSING>',
    latitude: '<MISSING>',
    longitude: '<MISSING>',
    hours_of_operation: '<MISSING>',
  };    
}
