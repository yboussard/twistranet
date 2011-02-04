commentOnSubmit = function(comments_container, ID) {
  var cform = jq('form', comments_container);
  var cUrl = home_url + "comment/" + ID + "/list.xml";
  cform.submit(function(e){
      e.preventDefault();
      e.stopPropagation();
      // it could be more simple,
      // but take care to remove the 'redirect_to' var
      data = {
        redirect_to : '',
        description: jq("textarea[name='description']", cform).val(),
        csrfmiddlewaretoken : jq("input[name='csrfmiddlewaretoken']", cform).val()
      };
      jq.post(cUrl, data, function(html) {
          loadComments(ID, html);
          // TODO : debug this ...
          // the django form returns by default the request value
          // so we remove it
          new_cform = jq('form', comments_container);
          jq("textarea[name='description']", new_cform).val("");
      });
      return false;
  });
}

loadComments = function(ID, html) {
    comments_container = jq("#view_comments"+ID);
    comments_container.empty();
    comments_container.prepend(html);
    jq("#view"+ID).remove();
    jq("#two_comments"+ID).remove(); 
    twistranet.showCommentsActions();
    commentOnSubmit(comments_container, ID);
    jq('a.confirmbefore', comments_container).click(function(e){
       e.preventDefault();
       initConfirmBox(this);
    } );
}


jq(function() 
{
  jq(".view_comments").click(function() 
  {
    var ID = jq(this).attr("id");
    
    jq.ajax({
      type: "GET",
      url: home_url + "comment/" + ID + "/list.xml",
      // data: "msg_id="+ ID, 
      cache: false,
      success: function(html){
        loadComments(ID, html);
      }
    });
    return false;
  });
});

