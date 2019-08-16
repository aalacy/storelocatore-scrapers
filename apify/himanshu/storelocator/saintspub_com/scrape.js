const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');

var url = 'https://saintspub.com/';

 
 
async function scrape(){
return new Promise(async (resolve,reject)=>{ 
request(url,(err,res,html)=>{

                    if(!err && res.statusCode==200){
                      
                          const $  =cheerio.load(html);
                          
                          var items=[];

                          var main =$('.et_builder_inner_content').children('div:nth-child(2)').find('.et_pb_text_inner');
                          function mainhead(i)

                          {
                              if(main.length>i)

                                  {


                            var link = main.eq(i).find('p:nth-child(4)').find('a').attr('href');

                            request(link,(err,res,html)=>{

                              if(!err && res.statusCode==200){

                                const $  =cheerio.load(html);

                                var main1 = $('#et-boc').find('.et_pb_text_inner').children('h3');

                                var hour_tmp = $('#et-boc').find('.et_pb_text_inner').find('p');
                                if(hour_tmp.length == 41){
                                  var hour = $('#et-boc').find('.et_pb_text_inner').find('p').slice(32,39).text();
                                  var phone = $('#et-boc').find('.et_pb_text_inner').find('p').last().text();
                                }
                               else if(hour_tmp.length == 30){
                                  var hour = $('#et-boc').find('.et_pb_text_inner').find('p').slice(21,28).text();
                                  var phone = $('#et-boc').find('.et_pb_text_inner').find('p').last().text();
                                }
                                else if(hour_tmp.length == 19){
                                var hour= $('#et-boc').find('.et_pb_text_inner').find('p').slice(9,17).text().replace('HOURS','');
                                var phone = $('#et-boc').find('.et_pb_text_inner').find('p').last().text(); 
                                }
                                else if(hour_tmp.length == 16){
                                var hour = $('#et-boc').find('.et_pb_text_inner').find('p').slice(6,13).text();
                                var phone = $('#et-boc').find('.et_pb_text_inner').find('p:nth-last-child(3)').text();  
                              }



                               

                                if(main1.length == 3){
                                  var location_name =  $('#et-boc').find('.et_pb_text_inner').children('h3:nth-child(1)').text();
                                  var tmp_address =  $('#et-boc').find('.et_pb_text_inner').children('h3:nth-child(2)').text();
                                  var tmp_address1 = tmp_address.split(',');
                                  var city = tmp_address1[1].trim();
                                  var address = tmp_address1[0];
                                  var state = tmp_address1[2].trim();
                                  
                                  
                                   
                                  

                                }

                                
                                else {
                                 var location_name = $('#et-boc').find('.et_pb_text_inner').children('h1:nth-child(1)').text();
                                 var tmp_address = $('#et-boc').find('.et_pb_text_inner').children('h1:nth-child(2)').text(); 
                                 
                                 if(tmp_address == ''){
                                   var tmp_address = $('#et-boc').find('.et_pb_text_inner').find('.entry-content').find('h3:nth-child(1)').text(); 
                                    
                                    } 
                                    var tmp_address1 = tmp_address.split(',');
                                    var city = tmp_address1[1].trim();
                                    var address = tmp_address1[0];
                                    var state = tmp_address1[2].trim();
                                    
                                   
                                
                                  
                                }

                                items.push({  

                                  locator_domain: 'https://saintspub.com/', 
                      
                                  location_name: location_name, 
                      
                                  street_address: address,
                      
                                  city: city, 
                      
                                  state: state,
                      
                                  zip: '<MISSING>',
                      
                                  country_code: 'US',
                      
                                  store_number: '<MISSING>',
                      
                                  phone: phone,
                      
                                  location_type: 'saintspub',
                      
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
  
                    mainhead(5);  
 

                }
       });
 
     
      })
    }
    Apify.main(async () => {

    

      const data = await scrape();
      
      await Apify.pushData(data);
       
    
    });
  