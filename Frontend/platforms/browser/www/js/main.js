var app = angular.module('Calhacks', []);

app.controller('mainCtrl', ['$scope', function($scope) {

	$scope.disable = true;
	$scope.fileNameChanged = function (elem) {
	  var file = elem;
	  document.getElementById("submit").removeAttribute("disabled");
	}

	$scope.submit = function() {
 	   var FR = new FileReader();
 	   FR.onload = function(e) {
 	   	$scope.uploadImage(e.target.result);
 	   };       
    FR.readAsDataURL( document.getElementById("file").files[0]);
	}

	$scope.uploadImage = function(img) {
		var imgdata = img.replace(/.*,/, '');
 	     $.ajax({
			url: "https://api.imgur.com/3/upload",
			type: "POST",
			datatype: "json",
			data: {image: imgdata},
			success: function(result) {
              var id = result.data.id;
              var url 'https://imgur.com/gallery/' + id;
            },
			beforeSend: function (xhr) {
			    xhr.setRequestHeader("Authorization", "Client-ID 47b80fa9d95a5be");
			}
		});;
	    
	}
}]);
