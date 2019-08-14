const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');

var url = 'https://www.cluckuchicken.com/Locations.aspx';

var url_temp = 'https://www.cluckuchicken.com';
 
 
async function scrape(){

return new Promise(async (resolve,reject)=>{
request(url,(err,res,html)=>{

                    if(!err && res.statusCode==200){
                      
                          const $  =cheerio.load(html);
                          
                          var items=[];

                          var main =$('#divLocationInformationListing').children('.divIndividualLocationContainer');

                          function mainhead(i)

                                      {
                                          if(main.length>i)

                                              {
                            var link =  url_temp + main.eq(i).find('a').attr('href');


                            request(link,(err,res,html)=>{

                              if(!err && res.statusCode==200){
                                
                                    const $  =cheerio.load(html);

                                    var location_name = $('.store-name').text();

                                    var address = $('.store-address-line1').text();
                                    var hour_tmp =  $('.divStoreBusinessHours').text().replace(/<[^>]*>?/gm, '').trim().replace(/\s/g,'').replace('DeliveryHours:Open-1/2hourbeforeclosingtime.LimitedDeliveryarea.','');
                                    var hour_tmp1 = hour_tmp.replace('WeDeliver!!!DeliveryHoursarefromOpenuntil1/2beforeclosingtimeOurDeliveryservicesarehandledbythirdparty.PricesandMenuitemsmayVary.Call-InorplaceorderonlineforPU.Whywaitinlineorderonline.www.cluckuchicken.com','');
                                    var hour_tmp2 = hour_tmp1.replace('DeliveryHours:Fromopen-1/2hourbeforeclosingtime','').replace('DeliveryHours:Opentill1/2hourbeforeclosingtime.','');
                                    var hour = hour_tmp2.replace('DeliveryHours:Opentill15minutesbeforeclosingtime.','').replace('Delivery:Open-tillclosingtimeUnderNewOwnership!!FreshFood,FreshVibe!!!','').replace('DeliveryHours:Open-1/2beforeclosingtime','');
                                    var phone = $('#ctl00_ContentPlaceHolder1_lblTelephone').text();
                                    
                                    var state_tmp  = $('.store-address-line2').text();
                                    var state_tmp1 =  state_tmp.split('-');
                                    var zip = state_tmp1[1];
                                    var city_tmp = state_tmp1[0];
                                    var city_tmp1 = city_tmp.split(' '); 

                                    if(city_tmp1.length == 4){

                                      var city = city_tmp1[0] + city_tmp1[1];
                                      var state = city_tmp1[2] + ' ' + city_tmp1[3].trim();


                                    }
                                    else if(city_tmp1.length == 3){

                                      var city = city_tmp1[0];
                                      
                                      var state_tmp = city_tmp1[1] +' ' + city_tmp1[2];

                                      var state = state_tmp.replace('STROUDSBURG','').replace('PARK','').trim();


                                    }
                                    else if(city_tmp1.length == 2){

                                      var city = city_tmp1[0];
                                      var state = city_tmp1[1].trim();


                                    }
                                     
                                     

                                    items.push({  

                                      locator_domain: 'https://www.cluckuchicken.com', 
                          
                                      location_name: location_name, 
                          
                                      street_address: address,
                          
                                      city: city, 
                          
                                      state: state,
                          
                                      zip:  zip,
                          
                                      country_code: 'US',
                          
                                      store_number: '<MISSING>',
                          
                                      phone: phone,
                          
                                      location_type: 'cluckuchicken',
                          
                                      latitude: '<MISSING>',
                          
                                      longitude: '<MISSING>', 
                          
                                      hours_of_operation: hour}); 
                          
                                      
                                      mainhead(i+1);


                              }

                            });
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
