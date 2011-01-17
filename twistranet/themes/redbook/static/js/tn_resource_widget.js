// reource widget helper
/**
 *
 * JQuery Helpers for Quick Upload
 *   
 */    

var TwistranetQuickUpload = {};
    
TwistranetQuickUpload.addUploadFields = function(uploader, domelement, file, id, fillTitles) {
    if (fillTitles)  {
        var labelfiletitle = jQuery('#uploadify_label_file_title').val();
        var blocFile = uploader._getItemByFileId(id);
        if (typeof id == 'string') id = parseInt(id.replace('qq-upload-handler-iframe',''));
        jQuery('.qq-upload-cancel', blocFile).after('\
                  <div class="uploadField">\
                      <label>' + labelfiletitle + '&nbsp;:&nbsp;</label> \
                      <input type="text" \
                             class="file_title_field" \
                             id="title_' + id + '" \
                             name="title" \
                             value="" />\
                  </div>\
                   ')
    }
    TwistranetQuickUpload.showButtons(uploader, domelement);
}

TwistranetQuickUpload.showButtons = function(uploader, domelement) {
    var handler = uploader._handler;
    if (handler._files.length) {
        jQuery('.uploadifybuttons', jQuery(domelement).parent()).show();
        return 'ok';
    }
    return false;
}

TwistranetQuickUpload.sendDataAndUpload = function(uploader, domelement, typeupload) {
    var handler = uploader._handler;
    var files = handler._files;
    var missing = 0;
    for ( var id = 0; id < files.length; id++ ) {
        if (files[id]) {
            var fileContainer = jQuery('.qq-upload-list li', domelement)[id-missing];
            var file_title = '';
            if (fillTitles)  {
                file_title = jQuery('.file_title_field', fileContainer).val();
            }
            uploader._queueUpload(id, {'title': file_title, 'typeupload' : typeupload});
        }
        // if file is null for any reason jq block is no more here
        else missing++;
    }
}    
TwistranetQuickUpload.onAllUploadsComplete = function(){
    Browser.onUploadComplete();
}
TwistranetQuickUpload.clearQueue = function(uploader, domelement) {
    var handler = uploader._handler;
    var files = handler._files;
    for ( var id = 0; id < files.length; id++ ) {
        if (files[id]) {
            handler.cancel(id);
        }
        jQuery('.qq-upload-list li', domelement).remove();
        handler._files = [];
        if (typeof handler._inputs != 'undefined') handler._inputs = {};
    }    
}    
TwistranetQuickUpload.onUploadComplete = function(uploader, domelement, id, fileName, responseJSON) {
    var uploadList = jQuery('.qq-upload-list', domelement);
    if (responseJSON.success) {        
        window.setTimeout( function() {
            jQuery(uploader._getItemByFileId(id)).remove();
            // after the last upload, if no errors, reload the page
            var newlist = jQuery('li', uploadList);
            if (! newlist.length) window.setTimeout( TwistranetQuickUpload.onAllUploadsComplete, 5);       
        }, 50);
    }
    
}

jQuery(
    function(){
        reswidget = jQuery('.resource-widget');
        theform = reswidget.parents('form');
        target_selector = jQuery('#selector_target', reswidget);
        if (target_selector.length) {
            theform.bind('submit', function(){
                 selectedfield = jQuery('.tnGrid input:checked', reswidget);
                 if (selectedfield.length) {
                     jQuery('#' + target_selector.val()).val(selectedfield.val());
                 }
                 target_selector.remove();
                 jQuery('input .tnGrid', reswidget).remove();
            })
            // when selecting a scope (account show the good pane)
            jQuery('#resourcepane-main .tnGridItem').click(function(e){
                var scope_id = jQuery('>input:hidden', this).val();
                jQuery('.resourcePane').hide();
                jQuery('#resourcepane-'+scope_id).fadeIn(1000);
            })
            
            // back to all accounts action
            jQuery('.resource-back-button').click(function(e){
                jQuery('.resourcePane').hide();
                jQuery('#resourcepane-main').fadeIn(500);
            })
            // calculate the good height 
            //it's important when displaying widget in a form to avod bad moving effects
            var selector_height = 0;
            jQuery('.tnGrid').each(function(){
                nbrows = jQuery('.tnGridRow', this).length ;
                new_height = 100*nbrows+20;
                if (new_height > selector_height) selector_height = new_height;
            });
            jQuery('#resources-selector').height(selector_height);
            // redefine the gridOnChange method
            // because we want to unselect all elements from all panels
            gridOnChange = function(grid) {
                jQuery('.resourcePane .tnGridItem').each(function(){
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
        }
    }
)