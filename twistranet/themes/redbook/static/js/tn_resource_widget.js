// resource widget helper    

var default_publisher_id = '';
var current_selection ='';
var new_selection='';
var selector = '';

showPreview = function(url, miniurl, legend) {
    newResultContainer = jQuery('#renderer-new');
    if (newResultContainer.length) {
        currentResultContainer = jQuery('#renderer-current');
        result= '\
<a class="image-block image-block-mini"\
   href="'+ url +'"\
   title="' + legend + '">\
   <img src="' + miniurl + '"\
        alt="' + legend + '" />\
</a>\
';
        jQuery('a', newResultContainer).remove();
        newResultContainer.append(result);
        newResultContainer.css('visibility', 'visible');
        if (currentResultContainer.length) currentResultContainer.animate({'opacity': '0.4'}, 500);
    }
}

hidePreview = function() {
    newResultContainer = jQuery('#renderer-new');
    if (newResultContainer.length) {
        currentResultContainer = jQuery('#renderer-current');
        jQuery('a', newResultContainer).remove();
        if (currentResultContainer.length) currentResultContainer.animate({'opacity': '1'}, 500);
    }
}

// load resources in json for a publisher (scope_id)
loadScopeResources = function(scope_id, selection) {
    scopeContainer = jQuery('#resourcepane-'+scope_id);
    scopeUrl = '/resource_by_publisher/json/';
    var tnGrid = jQuery('.tnGrid', scopeContainer);
    tnGrid.empty();
    jQuery.get(scopeUrl+scope_id+'?selection=' + selection, 
          function(data) {
              results = eval( "(" + data + ")" );
              jQuery(results).each(function() {
                  html = '\
<div class="tnGridItem">\
  <div class="thumbnail-account-part thumbnail-50-bottom">\
    <a href="' + this.url + '"\
       title="' + this.title + '"\
       class="image-block image-block-tile">\
      <img src="' + this.thumbnail_url + '"\
           alt="' + this.title + '" />\
    </a>\
    <label>\
      <a href="' + this.url + '">' + this.title + '</a>\
    </label>\
  </div>\
  <input type="radio"\
         name="grid-item-input"\
         class="grid-item-input"\
         value="' + this.id + '"\
         ' + this.selected + ' />\
  <input type="hidden"\
         name="grid-item-previewurl"\
         class="grid-item-previewurl"\
         value="' + this.preview_url + '" />\
  <input type="hidden"\
         name="grid-item-miniurl"\
         class="grid-item-miniurl"\
         value="' + this.mini_url + '" />\
</div>\
';
                  tnGrid.append(html);
              });
          gridStyle(tnGrid[0]);
          gridOnSelect(tnGrid[0]) ;
          widgetHeight();
          } );
    
}
// function called after upload or any change (imagine possible things in future))
// TODO put a wait loading icon
// TODO : global variable for reload (today reload = true when something has changed)
reloadScope = function(scope_id, selection, reload) {
    jQuery('.resourcePane').hide();
    jQuery('.resourcePane').removeClass('activePane');
    jQuery('#resourcepane-'+scope_id).addClass('activePane');
    if (reload) {
        loadScopeResources(scope_id, selection);
    }
    if (typeof uploadparams != 'undefined') uploadparams.publisher_id = scope_id;
    jQuery('#resourcepane-'+scope_id).fadeIn(1000);
}

// calculate the good height 
//it's important when displaying widget in a form to avoid bad moving effects
widgetHeight = function() {
    var selector_height = 0;
    jQuery('.tnGrid').each(function(){
        nbrows = jQuery('.tnGridRow', this).length ;
        new_height = 100*nbrows+20;
        if (new_height > selector_height) selector_height = new_height;
    });
    jQuery('#resources-selector').height(selector_height);
}

getActivePublisher = function() {
    return jQuery('.activePane input.scopeId').val();
}

// TODO : beurk jquery style like, make it pythonic
jQuery(
    function(){
        reswidget = jQuery('.resource-widget');
        theform = reswidget.parents('form');
        target_selector = jQuery('#selector_target', reswidget);
        if (target_selector.length) {      
            selector = jQuery('#' + target_selector.val());
            current_selection = selector.val();
            new_selection = selector.val();
            default_publisher_id = getActivePublisher();
            // remove input fields used by ajax requests only
            theform.bind('submit', function(){
                 target_selector.remove();
                 jQuery('.tnGrid input', reswidget).remove();
            })
            // preload resources in background
            jQuery('.resourcePaneFiles').each(function(){
                scope_id = jQuery('.scopeId', this).val();
                loadScopeResources(scope_id, current_selection);
            });
            // when selecting a scope (account) we show the good pane
            jQuery('#resourcepane-main .tnGridItem').click(function(e){
                var scope_id = jQuery('>input:hidden', this).val();
                jQuery('.resourcePane').hide();
                // TODO : change it ! the test is not perfect
                if (new_selection!=current_selection) reloadScope(scope_id, new_selection, true);
                else reloadScope(scope_id, new_selection, false);
            })
            
            // back to all accounts action
            jQuery('.resource-back-button').click(function(e){
                jQuery('.resourcePane').hide();
                jQuery('#resourcepane-main').fadeIn(500);
            })
            // redefine the gridOnChange method
            // because we want to unselect all elements from all panels
            gridOnChange = function(grid) {
                jQuery('.resourcePane .tnGridItem').each(function(){       
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
                if (! jQuery('.resourcePane .itemSelected').length) {
                    hidePreview();
                    new_selection = current_selection;
                }
                else {
                    itemselected = jQuery('.resourcePane .itemSelected')[0];
                    var checkbox = jQuery('>input:checkbox, >input:radio', itemselected);
                    new_selection = checkbox.val();
                    if (new_selection!=current_selection) {
                        showPreview(jQuery('a', itemselected).attr('href'), 
                                    jQuery('.grid-item-miniurl', itemselected).val(), 
                                    jQuery('a', itemselected).attr('title'));
                    }
                }
                selector.val(new_selection);
            }
            
        }
    }
)