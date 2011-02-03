/*
 * TwistraNet Main  javascript methods
 */


// global vars


var defaultDialogMessage = '';
var curr_url = window.location.href;
// live searchbox disparition effect
var ls_hide_effect_speed = 300;

// helpers

// set first and last class on subblocks
setFirstAndLast = function(block, sub, modulo) {
   jQuery(block).each(function() {
      if (typeof modulo=='undefined')  {
        jQuery(sub+':first', jQuery(this)).addClass('first');
        jQuery(sub+':last', jQuery(this)).addClass('last');
      }
      else {
        jQuery(sub, jQuery(this)).each(function(i) {
            if ((i+1)%modulo==0) jQuery(this).addClass('last');
            if ((i+1)%modulo==1) jQuery(this).addClass('first');
        })
      }
   })
}

// confirm boxes using jqueryui
initConfirmBox = function(elt){
    actionLabel = jQuery(elt).attr('title');
    actionLink = jQuery(elt).attr('href');
    dialogBox = jQuery('#tn-dialog');
    // the title of the box is kept using link title + ' ?'
    jQuery('#ui-dialog-title-tn-dialog').text(actionLabel+ ' ?');
    // the legend of the box is kept inside a invisible block with class 
    // confirm-message 
    // inside the link
    actionLegend = jQuery('.confirm-message', elt);
    if (actionLegend.length) jQuery('#tn-dialog-message').text(actionLegend.text());
    // translations for buttons are kept in the current page 
    // (could also be done using django javascript translations tools >> TODO)
    var cancelLabel = jQuery('#tn-dialog-button-cancel', dialogBox).text();
    var okLabel = jQuery('#tn-dialog-button-ok', dialogBox).text();
    var tnbuttons = {};  
    tnbuttons[okLabel] = function() {
      // ok action for now just redirect to the link
      window.location.replace(actionLink);
    };
    tnbuttons[cancelLabel] = function() {
      jQuery( this ).dialog( "close" );
    }; 
    dialogBox.dialog({   
      buttons: tnbuttons 
    });
    dialogBox.dialog('open');
}


escapeHTML = function(s) {
    return s.split('&').join('&amp;').split('<').join('&lt;').split('"').join('&quot;');
}
// absolutize url : the browser make the job
absolutizeURL = function(url) {
    var el= document.createElement('div');
    el.innerHTML= '<a href="'+escapeHTML(url)+'">x</a>';
    return el.firstChild.href;
}

// set selected class on a menu
// depending on current url
setSelectedTopic = function(menu) {   
    selected = false;
    jQuery('>ul>li', menu).each (function(i){
      topic = jQuery(this);
      jQuery('a', topic).each(function(){
          href = jQuery(this).attr('href'); 
          if (href && typeof href!='undefined' && ! selected) {
             if (absolutizeURL(href) == curr_url) { 
               selected = true;
               topic.addClass('selected');
               return false; }
          } 
      });
    });
    if (!selected) jQuery('>ul>li:first', menu).addClass('selected');
}

liveSearchDisplayResult = function(link, thumblink, type, title, description) {
    template= ' \
<div class="ls-result"> \
   <a href="' + link + '" \
      title="' + title + '" \
      class="image-block image-block-tile image-block-alone"> \
       <img src="' + thumblink + '" \
            alt="'+ title + '" /> \
   </a> \
  <p><span class="ls-result-title">' + title + '</span><span class="ls-result-type"> ' + type + '</span></p> \
  <p class="ls-result-description">' + description + '</p> \
  <div class="clear"><!-- --></div> \
</div> \
';    
// remove empty fields
template = template.replace('<span class="ls-result-type"> </span>', '');
template = template.replace('<span class="ls-result-title"></span>', '');
template = template.replace('<p></p>', '');
return template;
}



// Live search ajax
liveSearch = function(searchTerm) {
    livesearchurl = home_url + 'search/json' ;
    var liveResults = jQuery('#search-live-results');
    var nores_text = jQuery('#no-results-text').val();
    if (searchTerm) {
      jQuery.get(livesearchurl+'?q='+searchTerm, 
          function(data) {
              jsondata = eval( "(" + data + ")" );
              results = jsondata.results;
              liveResults.hide();
              liveResults.html('');
              if (results.length) {        
                  jQuery(results).each(function(){
                      html_result = liveSearchDisplayResult(this.link, this.thumb, this.type, this.title, this.description);
                      liveResults.append(html_result);
                  });
                  if (jsondata.has_more_results) {
                      html_more_results = '<div class="ls-result ls-allresults-link">';
                      html_more_results += '<a href="' + jsondata.all_results_url + '" title="' +  jsondata.all_results_text + '">';
                      html_more_results += jsondata.all_results_text + '</a>';
                      html_more_results += '<div class="clear"></div></div>';
                      liveResults.append(html_more_results);
                  }
                  allResults = jQuery('>.ls-result', liveResults);
                  lenResults = allResults.length;
                  allResults.each( function(){
                      var resBlock = jQuery(this);
                      resBlock.click( function(e){
                          jQuery("#search-text").unbind('focusout');
                          liveResults.stop();
                          location = jQuery('a', this).attr('href');
                      });
                      jQuery('a', resBlock).click(function(e){
                          e.preventDefault();
                          e.stopPropagation();
                          resBlock.trigger('click');
                          return false;
                      });
                  });
                  var activeResult = jQuery('.ls-result:first', liveResults);
                  activeResult.addClass('ls-result-active');       
                  var i = 0;
                  // live search results keyboard behavior
                  jQuery("#search-text").keydown(function(e){       
                      if (e.keyCode == '13') {
                          e.preventDefault();
                          e.stopPropagation();
                          activeResult.trigger('click');
                          return false;
                      }                          
                      else {
                          changes = false;
                          if (e.keyCode == '38' && i>0) {
                              e.preventDefault();
                              i-=1;       
                              changes = true;
                          }
                          else if ( e.keyCode == '40' && i<lenResults-1 ) {
                              e.preventDefault();
                              i+=1;           
                              changes = true;               
                          }
                          if (changes) {          
                              activeResult.removeClass('ls-result-active');
                              activeResult = jQuery(allResults[i]);
                              activeResult.addClass('ls-result-active');
                          }
                      }
                  });
                  setFirstAndLast('#search-live-results','.ls-result');
              }
              else {
                  liveResults.append('<p>' + nores_text + '</p>');
              }            
              liveResults.show(); 
          }
          );      
    }  
    else {
        liveResults.hide();
        liveResults.html('');
    } 
}


/* fix grid styles depending on Cols Number 
   the number is given by className
   ng  : 'tngridcols-9x' = 9 columns
 */

gridStyle = function(grid) {
    className = grid.className;
    /* define cols */
    if ( className.split('tngridcols-').length ) {
        ncols = parseInt(className.split('tngridcols-')[1].split('x')[0]);
        if (ncols) {
            jQuery('.tnGridItem', grid).each(function(i) {
                if ((i+1)%ncols==1) jQuery(grid).append('<div class="tnGridRow"></div>');
                gridRow= jQuery('.tnGridRow:last', grid);
                gridRow.append(jQuery(this));
                
            })
        }
    }            
    // see if something is selected
    gridOnChange(grid);
    // IMPORTANT : the grid is always shown at the end 
    // to avoid bad moving effect      
    jQuery(grid).css('display', 'table');
}

/* When something has changed on grid
   called on load or when selecting
   a radio button to check/uncheck elements */
   
gridOnChange = function(grid) {
    jQuery('.tnGridItem', grid).each(function(){
        var item = jQuery(this);       
        var checkbox = jQuery('>input:checkbox, >input:radio', this);
        if (checkbox.length) {
            if (checkbox.is(':checked')) {
                jQuery(this).addClass('itemSelected');
            }
            else {
                jQuery(this).removeClass('itemSelected');    
            }
        }
    });
}

/* actions on grid selection
   eg : check/uncheck value before submit */

gridOnSelect = function(grid) {
    jQuery('.tnGridItem', grid).each(function() {
        var item = jQuery(this);       
        var checkbox = jQuery('>input:checkbox, >input:radio', this);
        var radio = jQuery('>input:radio', this);
        if (checkbox.length) {
            item.click(function(e) {
                if (checkbox.is(':checked')) {
                    jQuery(this).removeClass('itemSelected');
                    checkbox.removeAttr("checked");
                }
                else {
                    checkbox.attr('checked', 'checked');
                    jQuery(this).addClass('itemSelected');
                }
                // for radios buttons unselect other items
                if (radio.length) gridOnChange(grid);
            })
        }
        jQuery('a', item).click(function(e) {
            e.preventDefault();
            e.stopPropagation();
            item.trigger("click");
        })
    })
}

// TODO in future : remove cache: true
// and improve ajax request with data 
// for multiple uploaders in a same page 
loadQuickUpload = function(obj) {
    var uploadUrl = home_url + '/resource_quickupload/' ;
    var tnUploader = jQuery(obj);
    jQuery.ajax({
        type: "GET",
        url: uploadUrl,
        dataType: 'html', 
        contentType: 'text/html; charset=utf-8', 
        cache: true,
        data: '',
        success: function(content){
            tnUploader.html(content);
        }
    });
}

var FileBrowserDialogue = {
    init : function () {
        // Here goes your code for setting your custom things onLoad.
    },
    submit : function (URL,title) {
        //var URL = document.my_form.my_field.value;
        var win = tinyMCEPopup.getWindowArg("window");

        // insert information now
        win.document.getElementById(tinyMCEPopup.getWindowArg("input")).value = URL;

        // are we an image browser
        if (typeof(win.ImageDialog) != "undefined") {
            // we are, so update image dimensions and title...
            if (win.ImageDialog.getImageData)
                win.ImageDialog.getImageData();
                win.document.getElementById('title').value = title;
                win.document.getElementById('alt').value = title;
            // ... and preview if necessary
            if (win.ImageDialog.showPreviewImage)
                win.ImageDialog.showPreviewImage(URL);
        }
        else win.document.getElementById('linktitle').value = title;

        // close popup window
        tinyMCEPopup.close();
    }
}

// main class
var twistranet = {
    browser_width: 0,
    browser_height: 0,
    __init__: function(e) {
        /* finalize styles */
        twistranet.setBrowserProperties();
        twistranet.finalizestyles();
        twistranet.showContentActions();
        twistranet.initconfirmdialogs();
        twistranet.initformserrors();
        twistranet.formsautofocus();
        twistranet.setEmptyCols(); 
        twistranet.enableLiveSearch();
        twistranet.prettyCombosLists(); 
        twistranet.tnGridActions();
        twistranet.formProtection();
        twistranet.loadUploaders();
        twistranet.initWysiwygBrowser();
    },
    setBrowserProperties : function(e) {
        if (! twistranet.browser_width){
            twistranet.browser_width = jQuery(window).width();
            twistranet.browser_height = jQuery(window).height();
        } 
    },
    prettyCombosLists: function(e) {
        // sexy combo list for permissions widget
        jQuery("select.permissions-widget").msDropDown();
        // remove the forced width (see also.dd .ddTitle in css) 
        jQuery(document).ready(function(){jQuery('.dd').css('width','auto')});
    },
    enableLiveSearch: function(e) {
        var defaultSearchText = jQuery("#default-search-text").val();
        searchGadget = jQuery("#search-text");                
        var liveResults = jQuery('#search-live-results');
        searchGadget.bind('focusin',function(){
            if (liveResults.html()!='') liveResults.show();
        });
        searchGadget.bind('focusout',function(){
            liveResults.delay(50).hide(ls_hide_effect_speed);
        });  
        if (searchGadget.length) {
            searchGadget.livesearch({
                searchCallback: liveSearch,
                innerText: defaultSearchText,
                queryDelay: 200,
                minimumSearchLength: 2
                });
        }
    },
    finalizestyles: function(e) {
        /* set some first and last classes  */
        jQuery([['.content-actions', 'li'],['#mainmenu > ul > li', '> ul> li'],['#content','.post']]).each(function(){
           setFirstAndLast(this[0], this[1]);
        } );         
        // set how many thumbs by line in different blocks
        jQuery([['.tn-box', '.thumbnail-50-bottom']]).each(function(){
           setFirstAndLast(this[0], this[1], 3);
        } );
        jQuery([['.tn-box', '.thumbnail-32-none']]).each(function(){
           setFirstAndLast(this[0], this[1], 5);
        } );   
        /* set selected topic in menus*/    
        setSelectedTopic(jQuery('#mainmenu'));
        /* set classes for some inline fields > todo : place it in template */
        jQuery('ul.inline-form #id_permissions, ul.inline-form #id_language, ul.inline-form :submit').each(function(){
          jQuery(this).parents('li').addClass('inlinefield');
        });
        /* finalize grids style */
        jQuery('.tnGrid').each(function(){
            gridStyle(this);
        });
    },
    setEmptyCols : function(e) {
        if (! $('#contextbar .tn-box-container:first').children().size() ) $('body').addClass('noleftcol');
    },
    showContentActions: function(e){
        /* show content actions on post mouseover */
        jQuery('.post').bind('mouseenter', function(){
          jQuery(this).addClass('activepost');
        });
        jQuery('.post').bind('mouseleave', function(){
          jQuery(this).removeClass('activepost');
        });                                          
    },
    initconfirmdialogs: function(e){
        if (jQuery('#tn-dialog-message').length) {
            defaultDialogMessage = jQuery('#tn-dialog-message').text();
            jQuery("#tn-dialog").dialog({  
              resizable: false,
              draggable: false,
              autoOpen: false,
              height: 120,
              width: 410,
              modal: true,
              close: function(ev, ui) { 
                jQuery('#tn-dialog-message').text(defaultDialogMessage);
                jQuery(this).hide(); 
              },
              focus: function(event, ui) { 
                ;
              }
            });
            links = 'a.confirmbefore';
            jQuery(links).click(function(e){
               e.preventDefault();
               initConfirmBox(this);
            } );       
        }
    },
    initformserrors: function(e) {
      jQuery('.fieldWrapper .errorlist').each(function(){
          jQuery(jQuery(this).parent()).addClass('fieldWrapperWithError');
      })
    },
    formsautofocus: function(e) {
     if (jQuery("form .fieldWrapperWithError :input:first").focus().length) return;
         jQuery("form.enableAutoFocus :input:visible:first").focus();
    },
    formProtection: function(e) {
        var form_has_changes = false;
        oform = jQuery('.enableUnloadProtect');
        if (oform.length) {
            jQuery('input, textarea, select', oform).change(function() {
                form_has_changes = true;
            });
            jQuery(oform).submit(function(){
                form_has_changes = false;
            });   
            jQuery('input[type=reset]',oform).click(function(){
                form_has_changes = false;
            });
            jQuery(window).bind('beforeunload', function(e){
                if (form_has_changes) {
                    // use the standard navigator beforeunload method
                    msg = jQuery('#form-protect-unload-message').html();
                    return msg;
                }
            })
        }
    },
    tnGridActions: function(e) {
     jQuery('.tnGrid').each(function(){
            gridOnSelect(this);
        });
    },
    loadUploaders: function(e) {
        jQuery('.tnQuickUpload').each(function(){
            loadQuickUpload(this);
        });
    },
    tinymceBrowser: function(field_name, url, type, win) {
        var cmsURL = '/resource_browser/?allow_browser_selection=1&type=' + type;    // script URL - use an absolute path!
        var browser_width = parseInt(twistranet.browser_width*70/100);     
        var browser_height = parseInt(twistranet.browser_height*90/100);
        tinyMCE.activeEditor.windowManager.open({
            file : cmsURL,
            title : 'Twistranet Browser',
            width : browser_width,  // Your dimensions may differ - toy around with them!
            height : browser_height,
            resizable : "yes",
            inline : "yes",  // This parameter only has an effect with inlinepopups plugin!
            close_previous : "no"
        }, {
            window : win,
            input : field_name
        });
        return false;
    },
    initWysiwygBrowser: function() {
        if (typeof tinyMCEPopup != 'undefined') tinyMCEPopup.onInit.add(FileBrowserDialogue.init, FileBrowserDialogue);
        // put here the code for other editors (ckeditor ....)
    }
}

jQuery(document).ready(twistranet.__init__)
