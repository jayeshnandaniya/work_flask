$('#customFile').on('change', function () {
	//get the file name
	var fileName = $(this).val();
	//replace the "Choose a file" label
	var cleanFileName = fileName.replace('C:\\fakepath\\', "");
	$(this).next('.custom-file-label').html(cleanFileName);
})
$('#customImage').on('change', function () {
	//get the file name
	var fileName = $(this).val();
	//replace the "Choose a file" label
	var cleanFileName = fileName.replace('C:\\fakepath\\', "");
	$(this).next('.custom-file-label').html(cleanFileName);
})
$('#profit_file').on('change', function () {
	//get the file name
	var fileName = $(this).val();
	//replace the "Choose a file" label
	var cleanFileName = fileName.replace('C:\\fakepath\\', "");
	$(this).next('.custom-file-label').html(cleanFileName);
})
$(document).ready(function () {


$('.new-user-add').click(function(){
   $('#error').text('');
  var password1= $('#InputPassword').val();
  var password2= $('#RepeatPassword').val();
        // If password not entered
        if (password1 == ''){
            $('#error').text('Please enter password');
              return false;
        }
        else if (password2 == ''){
           $('#error').text('Please enter confirm password');
            return false;
        }
        if(password1.length<5){
          $('#error').text('Please enter minimum 5 character');
            return false;
        }
        else if (password1 != password2) {
           $('#error').text('Password did not match: Please try again...');
            return false;
        }
});

	$('.view_docx_img').click(function () {
		jQuery('#PdfImageView').modal('show');
	});
	$('.upload-section').find(":input[type='file']").each(function (e) {
		var id = $(this).attr("id");
		var selectorFile = '#' + id;
		console.log(selectorFile, "ID");
		$(selectorFile).on('change', function () {
			//get the file name
			var fileName = $(this).val();
			//replace the "Choose a file" label
			var cleanFileName = fileName.replace('C:\\fakepath\\', "");
			$(this).next('.custom-file-label').html(cleanFileName);
		})
	});
	$("#add_another_button").click(function () {
		clone_field_list(".upload-section:last");
		update_delete_button();
	});
	$(".delete_button").click(function () {
		if ($(".upload-section").length > 1) {
			$(this).closest(".upload-section").remove();
		}
		update_delete_button();
	});
	update_delete_button();
});
function update_delete_button(selector) {
	if ($(".upload-section").length <= 1) {
		$(".delete_button").css("display", "none");
	} else {
		$(".delete_button").css("display", "initial");
	}
}
function clone_field_list(selector) {
	var new_element = $(selector).clone(true);
	console.log(new_element, 'new_element');
	var elem_id = new_element.find(":input")[0].id;
	console.log(elem_id, 'elem_id');
	var elem_num = parseInt(elem_id.replace(/.*-(\d{1,4})-.*/m, "$1")) + 1;
	console.log(elem_num, 'elem_num');
	new_element.find(":input[type='file']").each(function (i, obj) {
		// console.log(e,'Index');
		console.log($(this).attr("id"), 'ID');
		console.log("-" + (elem_num - 1) + "-", "Dash");
		console.log("-" + (elem_num) + "-", "Dash Replace");
		var id = $(this).attr("id").replace("-" + (elem_num - 1) + "-", "-" + elem_num + "-");
		$(this).attr({
			name: id,
			id: id,
		});
		if ($(this).attr("type") == "text" || $(this).attr("type") == "file") {
			if (jQuery("input[type='file']").length > 1) {
				if (i == 0) {
					$(this).next('.custom-file-label').html('Upload Back Test Report');
				} else {
					$(this).next('.custom-file-label').html('Upload Image');
				}
			} else {
				$(this).next('.custom-file-label').html('Upload Image');
			}
		}
	});
	new_element.find("label").each(function () {
		var new_for = $(this)
			.attr("for")
			.replace("-" + (elem_num - 1) + "-", "-" + elem_num + "-");
		$(this).attr("for", new_for);
	});
	$(selector).after(new_element);
}
