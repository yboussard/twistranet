// resource widget helper    



jQuery(
    function(){
        reswidget = jQuery('.resource-widget');
        theform = reswidget.parents('form');
        target_selector = jQuery('#selector_target', reswidget);
        if (target_selector.length) {
            theform.bind('submit', function(){
                 selectedfield = jQuery('.tnGrid input:checked', reswidget);
                 target_selector.remove();
                 jQuery('input .tnGrid', reswidget).remove();
            })
            // when selecting a scope (account) we show the good pane
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
            //it's important when displaying widget in a form to avoid bad moving effects
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
                            jQuery('#' + target_selector.val()).val(checkbox.val());
                        }
                        else {
                            jQuery(this).removeClass('itemSelected');
                            jQuery('#' + target_selector.val()).val();
                        }
                    }
                });
            }
        }
    }
)