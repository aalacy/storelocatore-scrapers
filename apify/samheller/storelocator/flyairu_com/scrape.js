const Apify = require('apify');
const axios = require('axios');
const jsdom = require("jsdom");
const { JSDOM } = jsdom;

Apify.main(async () => {
  const links = await pageList();
  for (let l of links){
    data = await axios({
      method: "GET",
      url: l.url
    }).then(async (resp) => {
      dom = await getDom(resp.data);
      hoursUrl = l.url + dom.querySelector('.contact-block > .hours > a').getAttribute('href')
      
      data = {};
      data.addr =  dom.querySelector('.contact-block > .address').textContent.trim().split("\n")
      data.phone = dom.querySelector('.contact-block > .phone').textContent.trim();
      data.hours = await getHours(hoursUrl);
      data.locationName = l.url.replace(/^.*airu-/, '').replace(/\.com.*/, '');
      
      return data;
    })
    
    poi = getRecord('flyairu.com');
    poi.location_name = data.locationName;
    poi.street_address = data.addr[0];
    poi.phone = data.phone;
    poi.hours_of_operation = data.hours;

    //Retrieve city by splitting on ,
    area = data.addr[1].trim().split(',');
    poi.city = area[0];

    //Retrieve Zip by splitting on whitespace and grabbing last
    area = area[1].split(" ");
    poi.zip = area.pop();

    //Remaining is State
    poi.state = area.join(" ");

    await Apify.pushData([poi])
  }
});

async function pageList(){
  return await axios({
    method: "GET",
    url: "https://flyairu.com/"
  }).then((resp) => {
    dom = getDom(resp.data);
    links = [];
    for (let l of dom.querySelectorAll('ul.map-list > li > a')){
        links.push({url: l.getAttribute('href')})
    }
    return links;
  })
}

async function getHours(hoursUrl){
  return await axios({
      method: "GET",
      url: hoursUrl
    }).then((resp) => {
      ret = [];
      hrsDom = getDom(resp.data)
      for (let hr of hrsDom.querySelectorAll('.hours_table')[1].querySelectorAll('tbody > tr')){
        if (/[A-Z]{3,6}day:/gi.test(hr.textContent)){
          ret.push(hr.textContent);
        }
      }
      return ret.join(", ");
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
