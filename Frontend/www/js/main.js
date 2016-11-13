var app = angular.module('Calhacks', []);

app.controller('mainCtrl', ['$scope', function($scope) {

$scope.shapes = [];

$scope.loading = false;
$scope.finalData = [];
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
			    xhr.setRequestHeader("Authorization", "Client-ID 23beebdb5fe43d5");
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
              $scope.finalData = result;
              $scope.loading = false;
              $scope.changeData();
              $scope.$apply();
            }, error : function(r) {
            	console.log(r);
            	$scope.loading = false;
            	$scope.$apply();
            }
		});;
	}

	$scope.changeData = function() {
		$scope.lst1 = [];
		$scope.lst2 = [];
		$scope.lst3 = [];

		for (var i=0; i < $scope.finalData.items.length; i++) {
			if ($scope.finalData.items[i][0].startsWith("*")) {
				$scope.lst1.push($scope.finalData.items[i]);
			}
		} 
		for (var i=0; i < $scope.finalData.items.length; i++) {
			if ($scope.finalData.items[i][0].startsWith("#")) {
				$scope.lst2.push($scope.finalData.items[i]);
			}
		} 
		for (var i=0; i < $scope.finalData.items.length; i++) {
			if ($scope.finalData.items[i][0].startsWith("^")) {
				$scope.lst3.push($scope.finalData.items[i]);
			}
		} 
		$scope.shapes = [$scope.lst1, $scope.lst2, $scope.lst3];
		console.log($scope.shapes)
		
	}


}]);
