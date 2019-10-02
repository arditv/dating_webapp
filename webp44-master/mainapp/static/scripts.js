//Static javascript file which will be imported to html files
function checkuseranswer(data, textStatus, jqHXR) {
  console.log(data)
   	$('#info').html(data);
   }
   function f(page) {
     console.log($('input[name=username]').val())
     console.log($('input[name=csrfmiddlewaretoken]').val())
     console.log(page)
		$.ajax({
			type: 'POST',
			url: '/checkuser/',
			data : {
				'username' : $('input[name=username]').val(),
				'csrfmiddlewaretoken' : $('input[name=csrfmiddlewaretoken]').val(),
            'page' : page,
			},
			success: checkuseranswer,
			dataType: 'html',
      });
	}
	$('.registerusername').blur(function() { f('createAccount'); });
	$('.loginusername').blur(function() { f('login'); });
