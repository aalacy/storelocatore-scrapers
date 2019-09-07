const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');
 
 
 
var url = 'http://www.salo-salogrill.com/locations';
async function scrape(){

  return new Promise(async (resolve,reject)=>{
 
request(url,(err,res,html)=>{

  if(!err && res.statusCode==200){
   
     const $  =cheerio.load(html);
        var items=[];
        var location_name = $('#ctl01_ctl00_description').find('h3').text().replace('Hours','').trim();
        var main = $('.clearfix').find('#ctl01_rptAddresses_ctl00_addrlocation');
       function mainhead(i)

                    {
                        if(main.length>i)

                            {
        
        var address = $('.clearfix').find('#ctl01_rptAddresses_ctl00_addrlocation').eq(i).find('#ctl01_rptAddresses_ctl00_pAddressInfo').text().replace(',','').trim();
        var city_tmp = $('.clearfix').find('#ctl01_rptAddresses_ctl00_addrlocation').eq(i).find('#ctl01_rptAddresses_ctl00_pStateZip').text();
        var city_tmp1 = city_tmp.split(',');
        var city = city_tmp1[0];
        var state_tmp = city_tmp1[1].split(' ');
        var state = state_tmp[1];
        var zip = state_tmp[2];
        var hour = $('#ctl01_ctl00_description').find('p').text();
        

        var phone = $('.clearfix').find('#ctl01_rptAddresses_ctl00_addrlocation').eq(i).find('#ctl01_rptAddresses_ctl00_pPhonenum').text().replace('Phone.','');
                    items.push({
                      locator_domain : 'http://www.salo-salogrill.com/',
                      location_name : location_name,
                      street_address : address,
                      city:city,
                      state:state,
                      zip:zip,
                      country_code: 'US',
                      store_number:'<MISSING>',
                      phone:phone,
                      location_type:'salo-salogrill',
                      latitude:'<MISSING>',
                      longitude :'<MISSING>',
                      hours_of_operation:hour
                      
                      });  
          mainhead(i+1);

        }


         else{
    
        resolve(items);
    
          }
        } 

       mainhead(0);
         
            }
    });
  });
}

  
    
   
  
  Apify.main(async () => {
  
     const data = await scrape();
     await Apify.pushData(data);
    
    });