var app = angular.module('Calhacks', []);

app.controller('mainCtrl', ['$scope', function($scope) {

	$scope.disable = true;
	$scope.fileNameChanged = function (elem) {
	  var file = elem;
	  document.getElementById("submit").removeAttribute("disabled");
	}

}]);