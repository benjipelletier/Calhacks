var app = angular.module('Calhacks', []);

app.controller('mainCtrl', ['$scope', function($scope) {

$scope.loading = false;

	$scope.disable = true;
	$scope.fileNameChanged = function (elem) {
	  var file = elem;
	  document.getElementById("submit").removeAttribute("disabled");
	}

	$scope.submit = function() {
		$scope.loading = true;
 	   var FR = new FileReader();
 	   FR.onload = function(e) {
 	   	$scope.uploadImage(e.target.result);
 	   };       
    FR.readAsDataURL( document.getElementById("file").files[0]);
	}

	$scope.uploadImage = function(img) {
		var imgdata = img.replace(/.*,/, '')
 	     $.ajax({
			url: "https://api.imgur.com/3/upload",
			type: "POST",
			datatype: "json",
			data: {image: imgdata},
			success: function(result) {
              var id = result.data.id;
              $scope.submitLink('http://i.imgur.com/' + id + '.jpg');
            },
			beforeSend: function (xhr) {
			    xhr.setRequestHeader("Authorization", "Client-ID 47b80fa9d95a5be");
			}
		});;
	    
	}
		$scope.submitLink = function(url) {
		$.ajax({
			url: "http://162.243.140.149:5000/",
			type: "GET",
			data: {data: url},
			success: function(result) {
              console.log(result);
              $scope.loading = false;
            }, error : function(r) {
            	console.log(r);
            	$scope.loading = false;
            }
		});;
	}
}]);
