$(document).ready(function(){
    // enable tabbing using JS
    $('#myTab a').click(function(e){
        e.preventDefault();
        $('.sub-pagleft').hide();
        
        $(this).tab('show');
        $($(this).attr("href") + " .sub-pagleft").show();
        
    });

    $('#memberSearch').submit(function(e){
        e.preventDefault();
        var search_value = $("[name=search]").val();
        var data = $(this).serialize();

        $.ajax({
            data: data,
            url: "/dashboard/search/",
            type: "POST",
            success: function(result){
                var json = $.parseJSON(result);

                // create H1 element with contents
                var h1 = document.createElement('h1');
                var h1_content = "Search results for «" + search_value + "»";
                $(h1).text(h1_content);

                var ul = document.createElement('ul');

                $.each(json, function(index, value){
                    // create an li element per item listed in the JSON response
                    // then append it to the ul element
                    var li = document.createElement('li');
                    $(li).text(value['fields']['person']['fields']['user']['fields']['username']);
                    $(ul).append(li);
                });

                moveTabsAndContents();
                var page = {title: h1_content, content: ul};
                load_page(page);

            }
        });
    });
});