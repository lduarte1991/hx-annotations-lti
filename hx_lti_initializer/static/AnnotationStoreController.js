var AnnotationStoreController = function(deferredObject){
	if (this.constructor === AnnotationStoreController) {
		throw new Error("Can't instantiate abstract class");
	}
};

AnnotationStoreController.prototype.getDatabaseEndPoint = function() {
	throw new Error("Abstract method!");
};

AnnotationStoreController.prototype.getNumOfAnnotationsOnScreen = function(){
	throw new Error("Abstract method!");
};

AnnotationStoreController.prototype.setUpListener = function(listener, expected_fun) {
	throw new Error("Abstract method!");
};

AnnotationStoreController.prototype.updateMasterList = function(focus_id, viewer){
	throw new Error("Abstract method!");
};

AnnotationStoreController.prototype.updateEndpointList = function() {
	throw new Error("Abstract method!");
};

AnnotationStoreController.prototype.loadMoreAnnotations = function(annotations) {
	throw new Error("Abstract method!");
};

AnnotationStoreController.prototype.addNewAnnotationToMasterList = function(annotation) {
	throw new Error("Abstract method!");
};

AnnotationStoreController.prototype.removeAnnotationFromMasterList = function(annotation) {
	throw new Error("Abstract method!");
};

AnnotationStoreController.prototype.updateAnnotationInMasterList = function(annotation) {
	throw new Error("Abstract method!");
};

AnnotationStoreController.prototype.getAnnotationById = function(id) {
	throw new Error("Abstract method!");
};

AnnotationStoreController.prototype.authorize = function(action, annotation) {
	throw new Error("Abstract method!");
};

AnnotationStoreController.prototype.openEditorForReply = function(location) {
	throw new Error("Abstract method!");
};

AnnotationStoreController.prototype.deleteAnnotation = function(annotation) {
	throw new Error("Abstract method!");
};

AnnotationStoreController.prototype.editAnnotation = function(annotation, button) {
	throw new Error("Abstract method!");
};

AnnotationStoreController.prototype.loadRepliesForParentAnnotation = function(annotation_id, displayFunction) {
	throw new Error("Abstract method!");
};

AnnotationStoreController.prototype.deleteReply = function(reply, callback) {
	throw new Error("Abstract method!");
};

/***
 ** Annotator Endpoint for Dashboard Interaction
 **
 ** Provides a way for the DashboardController.js to interact with the database via Annotator.
 ***/
var AnnotatorEndpointController = function(deferredObject) {
    AnnotationStoreController.apply(this, arguments);

    // gets the current instance of the wrapper around the target object and annotator
	var wrapper = jQuery('.annotator-wrapper').parent()[0];
	this.annotator = jQuery.data(wrapper, 'annotator');
	this.annotationsMasterList = [];
	deferredObject.resolve();
	this.queryDefault = {
		user_id: undefined,
		media: "text",
	};

};

AnnotatorEndpointController.prototype = Object.create(AnnotationStoreController.prototype);

AnnotatorEndpointController.prototype.constructor = AnnotatorEndpointController;

AnnotatorEndpointController.prototype.getDatabaseEndPoint = function() {
	return this.annotator;
};

AnnotatorEndpointController.prototype.getNumOfAnnotationsOnScreen = function (){
	return this.annotator.plugins.Store.annotations.length;
};

AnnotatorEndpointController.prototype.setUpListener = function(listener, expected_fun) {
	var self = this;
	var annotator = this.annotator;

	annotator.subscribe(listener, function(annotations) {
		//console.log(listener + "Triggered! ");
		expected_fun(annotations);
	});
};

AnnotatorEndpointController.prototype.updateMasterList = function(focus_id, viewer) {
	var self = this;
	var searchParameters = this.annotator.plugins.Store.options.loadFromSearch;
	searchParameters.limit = -1;
	searchParameters.offset = 0;
	var onSuccess = function(data) {
		if (data === null) {
			data = {}
		};
		if (typeof focus_id !== "undefined") {
			data.rows.forEach(function(annotation){
				var focus = parseInt(focus_id, 10);
				if (annotation.id === focus) {
					self.annotationsMasterList = [annotation];
					self._clearAnnotator({ except: [annotation] });
					viewer.clearDashboard();
					viewer.updateDashboard(0, 1, [annotation], false);
				};
			})
		} else {
			self.annotationsMasterList = data.rows || [];
		}
	};
	search_url = this.annotator.plugins.Store._urlFor("search");
	var options = this.annotator.plugins.Store._apiRequestOptions("search", searchParameters, onSuccess);
	var request = jQuery.ajax(search_url, options);
};

AnnotatorEndpointController.prototype.updateAnnotationInMasterList = function(annotation) {
	for (index in this.annotationsMasterList) {
		if (this.annotationsMasterList[index].id === annotation.id)
			this.annotationsMasterList[index] = annotation;
	}
}

AnnotatorEndpointController.prototype.updateEndpointList = function(options) {
	// will never differ from annotator
};

AnnotatorEndpointController.prototype.loadMoreAnnotations = function(annotations) {
	var self = this;
	annotations.forEach(function(annotation){
		self.annotator.setupAnnotation(annotation);
		self.annotator.plugins.Store.registerAnnotation(annotation);
		self.updateAnnotationInMasterList(annotation);
	});
	self.annotator.publish("externalCallToHighlightTags");
};

AnnotatorEndpointController.prototype.addNewAnnotationToMasterList = function(annotation) {
	this.annotationsMasterList.unshift(annotation);
};

AnnotatorEndpointController.prototype.removeAnnotationFromMasterList = function(annotation) {
    var found = -1;
    this.annotationsMasterList.forEach(function(ann, index) {
        if (annotation.id === ann.id) {
            found = index;
        };
    });
    if (found > -1) {
        this.annotationsMasterList.splice(found, 1);
        return false;
    };
    return true;
};

AnnotatorEndpointController.prototype.getAnnotationById = function(id) {
	var annotationId = parseInt(id, 10);
	var annotations = this.annotationsMasterList;
	var currentAnnotations = this.annotator.plugins.Store.annotations;
	for (var index in currentAnnotations){
		if  (currentAnnotations[index].id === annotationId){
			return currentAnnotations[index];
		}
	}

	for (var index in annotations) {
		if (annotations[index].id === annotationId)
			return annotations[index];
	}

	return undefined;
};

AnnotatorEndpointController.prototype.authorize = function(action, annotation) {
	var permissions = this.annotator.plugins.Permissions;
	return permissions.options.userAuthorize(action, annotation, permissions.user);
};

AnnotatorEndpointController.prototype.openEditorForReply = function(location) {
	var position = {
		display: "block",
		left: location.left,
		top: location.top,
	};
	this.annotator.adder.css(position);
	this.annotator.onAdderClick();

	var parent = jQuery(this.annotator.editor.element).find('.reply-item span.parent-annotation');
    parent.html(annotation_id);
};

AnnotatorEndpointController.prototype.deleteAnnotation = function(annotation) {
	this.updateAnnotationInMasterList(annotation);
	this.annotator.deleteAnnotation(annotation);
};

AnnotatorEndpointController.prototype.editAnnotation = function(annotation, button) {
	var self = this;

	var options = {
		focus: true,
		width: "100%",
		airMode: true,
	};

	jQuery('.parentAnnotation .body').summernote(options);
	jQuery('.parentAnnotation .body').css({
		"outline": "1px solid white",
    	"margin-right": "10px",
    	"margin-bottom": "10px",
    	"padding": "3px",
    	"border": "2px solid gray",
	});
	jQuery('.parentAnnotation .editgroup').hide();
	jQuery('.parentAnnotation .savegroup').show();

	var currentBody = jQuery('.parentAnnotation .body').html();
	jQuery('.parentAnnotation .body').code(currentBody);
	var annotation_to_update = annotation;
	var closeEditingMode = function(){
		jQuery('.parentAnnotation .body').css({
			"outline": "0px",
	    	"margin-right": "0px",
	    	"margin-bottom": "0px",
	    	"padding": "0px",
	    	"border": "0px",
		});
		jQuery('.parentAnnotation .editgroup').show();
		jQuery('.parentAnnotation .savegroup').hide();
		if (jQuery('.parentAnnotation .body').summernote !== undefined) {
			jQuery('.parentAnnotation .body').destroy();
		} else if(tinymce !== undefined){
			tinymce.remote();
		}
	};

    jQuery('.parentAnnotation .savegroup #save').click(function(e) {
		annotation_to_update.text = jQuery('.parentAnnotation .body').code();
		self.annotator.updateAnnotation(annotation_to_update);

		closeEditingMode();
	});

	jQuery('.parentAnnotation .savegroup #cancel').click(function(e) {
		closeEditingMode();
		jQuery('.parentAnnotation .body').html(currentBody);
	});

};

AnnotatorEndpointController.prototype.loadRepliesForParentAnnotation = function(annotation_id, displayFunction) {
	var anId = parseInt(annotation_id, 10);
	var self = this;
	var annotator = self.annotator;
	var store = annotator.plugins.Store;
	var oldLoadFromSearch = annotator.plugins.Store.options.loadFromSearch;
	var annotation_obj_id = oldLoadFromSearch.uri;
	var context_id = oldLoadFromSearch.contextId;
	var collection_id = oldLoadFromSearch.collectionId;

	var newLoadFromSearch = {
		limit: -1,
		parentid: anId,
		media: "comment",
		uri: annotation_obj_id,
		contextId: context_id,
		collectionId: collection_id,
	};

	var onSuccess = function(data) {
		if (data === null) {
			data = {};
		}
		self.list_of_replies = data.rows || [];
		displayFunction(self.list_of_replies);
	}

	search_url = store._urlFor("search", annotation_id);
    var options = store._apiRequestOptions("search", newLoadFromSearch, onSuccess);
    jQuery.ajax(search_url, options);

};

AnnotatorEndpointController.prototype.deleteReply = function(reply, callback) {
	this.annotator.plugins.Store._apiRequest("destroy", reply, callback);
};

AnnotatorEndpointController.prototype.queryDatabase = function(options, pagination, mediaType) {
	var setOptions = jQuery.extend({}, this.queryDefault, options);
	var annotator = this.annotator;

	// TODO: Change below to be a call to the Core Controller
	var loadFromSearch = annotator.plugins.Store.options.loadFromSearch;
	var numberOfAnnotations = jQuery('.annotationSection .annotationItem').length;
	loadFromSearch.limit = pagination;
	loadFromSearch.offset = 0;
	loadFromSearch.media = mediaType;
	loadFromSearch.userid = setOptions.user_id;
	loadFromSearch.username = setOptions.username;
	loadFromSearch.text = setOptions.text;
	loadFromSearch.tag = setOptions.tag;
	this._clearAnnotator();
	annotator.plugins.Store.loadAnnotationsFromSearch(loadFromSearch);
};

// TODO (Move to Annotator Core)
AnnotatorEndpointController.prototype._clearAnnotator = function(options) {
    options = options || {};
    var annotator = this.annotator;
    var store = annotator.plugins.Store;
    var annotations = store.annotations.slice();
    var except = options.except || []; // array of annotations that should *NOT* be cleared
    var except_ids = jQuery.map(except, function(anno) { return anno.id; });
    
    annotations.forEach(function(ann){
        var child, h, _i, _len, _ref;
        if (except_ids.indexOf(ann.id) >= 0) {
            return;
        }
        if (ann.highlights !== undefined) {
            _ref = ann.highlights;
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
                h = _ref[_i];
                if (!(h.parentNode !== undefined)) {
                    continue;
                }
                child = h.childNodes[0];
                jQuery(h).replaceWith(h.childNodes);
            }
        }
        store.unregisterAnnotation(ann);
    });
};

AnnotatorEndpointController.prototype._showAnnotations = function(annotations) {
    var annotator = this.annotator;
    var store = annotator.plugins.Store;
    var annotations = annotations;
    
    annotations.forEach(function(ann){
        annotator.publish('annotationCreated', [ann]);
    });
};


/***
 ** Mirador Endpoint for Dashboard Interaction
 **
 ** Provides a way for the DashboardController.js to interact with the database via Mirador.
 ***/

var MiradorEndpointController = function(deferredObject) {
    AnnotationStoreController.apply(this, arguments);
    var self = this;
    mir.eventEmitter.subscribe('windowAdded', function (event, windowId, slotAddress) {
    	//console.log("window was added");
    	// TODO (check id to make sure slot/window match initialized)
    	self.window = mir.viewer.workspace.slots[0].window;
		self.endpoint = self.window.endpoint;
		deferredObject.resolve();
		mir.eventEmitter.subscribe('annotationsRendered.' + self.window.id, function() {
			var annotations = self.window.annotationsList;
			if (annotations !== undefined && annotations !== null && annotations.length > 0) {
				window.AController.main.colorizeAnnotations(annotations);
			};
		});
		mir.eventEmitter.subscribe('tooltipViewerSet.' + self.window.id, function (){
			window.AController.main.colorizeViewer();
		});
		mir.eventEmitter.subscribe('annotationEditorAvailable.' + self.window.id, function (){
			var tagElements = jQuery('#annotation-editor-'+self.window.id).find('.tags-editor');
			if (typeof window.AController.main.tags !== "undefined") {
				tagList = [];
				Object.keys(window.AController.main.tags).forEach(function(tag){
					tagList.push({'id': tag, 'name': tag});
				});
				tagElements.tokenInput(tagList);
				jQuery('#token-input-tags-editor' + self.window.id).attr('placeholder', "Add tag...");
			};
			if (typeof tagElements.attr("value") !== "undefined") {
				var existingTags = tagElements.attr("value").split(" ");
				existingTags.forEach(function(item) {
					tagElements.tokenInput("add", {"id": item, "name": item});
				});
				window.AController.targetObjectController.colorizeEditor();
			};
		});
		self.imageLimits = {};
		var currentId = self.window.canvasID;
		jQuery.each(self.window.imagesList, function(index, value) {
			if (value['@id'] == currentId) {
				self.imageLimits['height'] = value.height;
				self.imageLimits['width'] = value.width;
			};
		});
		mir.eventEmitter.subscribe('imageRectangleUpdated', function(event, options){
			if (options.id == self.window.id) {
				var xChecked = options.osdBounds.x;
				var yChecked = options.osdBounds.y;
				var heightChecked = options.osdBounds.height;
				var widthChecked = options.osdBounds.width;
				if (xChecked < 0) {
					xChecked = 0;
				}
				if(heightChecked > self.imageLimits.height){
					heightChecked = self.imageLimits.height;
				}
				if (yChecked < 0) {
					yChecked = 0;
				}
				if(widthChecked > self.imageLimits.width){
					widthChecked = self.imageLimits.width;
				}

				self.currentImageBounds = {
					"height": heightChecked.toString(),
					"width": widthChecked.toString(),
					"x": xChecked.toString(),
					"y": yChecked.toString(),
				};
				
			};
		});
	});
	self.annotationsMasterList = [];
	self.queryDefault = {
		user_id: undefined,
		media: "image",
	};

};    

MiradorEndpointController.prototype = Object.create(AnnotationStoreController.prototype);

MiradorEndpointController.prototype.constructor = MiradorEndpointController;

MiradorEndpointController.prototype.getDatabaseEndPoint = function() {
	return this.endpoint;
};

MiradorEndpointController.prototype.getNumOfAnnotationsOnScreen = function (){
	return this.window.annotationsList.length;
};

MiradorEndpointController.prototype.setUpListener = function(listener, expected_fun) {
	var self = this;
	if (listener === "catchAnnotationsLoaded") {
		mir.eventEmitter.subscribe(listener + '.' + self.window.id, function(event) {
			var annotations = self.endpoint.annotationsListCatch;
			expected_fun(annotations);
			
		});
	} else {
		mir.eventEmitter.subscribe(listener + '.' + self.window.id, function(event, annotation) {
			expected_fun(annotation);
		});
	}
};

MiradorEndpointController.prototype.updateMasterList = function(focus_id, viewer){
	// make a call to mirador endpoint to call CATCH to get a new instance
	this.annotationsMasterList = this.endpoint.annotationsListCatch.slice();
	if (typeof focus_id !== "undefined") {
		var annotation = this.getAnnotationById(focus_id);
		var self = this;
		self.window.annotationsList = [self.endpoint.getAnnotationInOA(annotation)];
		//mir.eventEmitter.publish('annotationListLoaded.' + self.window.id);
		mir.eventEmitter.publish('ANNOTATIONS_LIST_UPDATED', {windowId: self.window.id, annotationsList: self.window.annotationsList});
		try{
			mir.eventEmitter.publish('fitBounds.' + self.window.id, annotation.bounds);
		} catch (e){
			mir.eventEmitter.subscribe('osdOpen.' + self.window.id, function(){
				mir.eventEmitter.publish('fitBounds.' + self.window.id, annotation.bounds);
			});
		}
		
		viewer.updateDashboard(0, 1, [annotation], false);

	}
};

MiradorEndpointController.prototype.updateEndpointList = function(options){
	if (options.limit) {
		this.window.annotationsList = this.window.annotationsList.slice(0, options.limit);
		//mir.eventEmitter.publish('annotationListLoaded.' + this.window.id);
		mir.eventEmitter.publish('ANNOTATIONS_LIST_UPDATED', {windowId: this.window.id, annotationsList: this.window.annotationsList});
	};
};

MiradorEndpointController.prototype.loadMoreAnnotations = function(annotations) {
	var self = this;
	//console.log("Load Annotations");
	//console.log(annotations);
	annotations.forEach(function(annotation){
		// Add annotations to annotationListCatch
		self.endpoint.annotationsListCatch.push(annotation);
		var oaAnnotation = self.endpoint.getAnnotationInOA(annotation);
		// trigger drawing here or once they're all loaded below
		self.window.annotationsList.push(oaAnnotation);
	});
	//mir.eventEmitter.publish('annotationListLoaded.' + self.window.id);
	mir.eventEmitter.publish('ANNOTATIONS_LIST_UPDATED', {windowId: self.window.id, annotationsList: self.window.annotationsList});
	// trigger only after adding all items to annotationListCatch
};

MiradorEndpointController.prototype.addNewAnnotationToMasterList = function(annotation){
	if (annotation.media === "comment") {
		this.list_of_replies[annotation.id] = annotation;
	} else {
		this.annotationsMasterList.unshift(annotation);
		var notfound = true;
		for(ann in this.endpoint.annotationsListCatch) {
			if (ann.id == annotation.id) {
				notfound = false;
			}
		}
		if (notfound) {
			this.loadMoreAnnotations([annotation]);
		}
	}
};

MiradorEndpointController.prototype.removeAnnotationFromMasterList = function(annotation){
	var annotation_checked = annotation;

	if (typeof annotation_checked !== "object") {
		annotation_checked = this.getAnnotationById(annotation_checked);
	};

	var index = this.annotationsMasterList.indexOf(annotation_checked);
	
	if (index > -1) {
		this.annotationsMasterList.splice(index, 1);
		return false;
	};
	return true;
};

MiradorEndpointController.prototype.getAnnotationById = function(id) {
	var annotationId = parseInt(id, 10);
	var annotations = this.annotationsMasterList;

	for (index in annotations) {
		if (annotations[index].id === annotationId)
			return annotations[index];
	}

	return undefined;
};

MiradorEndpointController.prototype.authorize = function(action, annotation) {
	var user = this.endpoint.catchOptions.user;
	var permissions = this.endpoint.catchOptions.permissions;
	var tokens = annotation.permissions[action] || [];
	if (tokens.length === 0) {
		return true;
	}
	for (item in tokens) {
		var token = tokens[item];
		if (user.id === token) {
			return true;
		}
	}
	return false;
};

MiradorEndpointController.prototype.openEditorForReply = function(options) {
	//given location = {top:, left:}, open an editor to be able to reply here
	var repliesList = options.repliesList;
	var template = options.templateReply;
	var self = this;
	repliesList.prepend(template);
	tinymce.init({ 
		selector:".replyItemEdit .replyText", 
		inline: true, 
		menubar: false,
		plugins: "image link media",
        statusbar: false,
        toolbar_items_size: 'small',
        toolbar: "bold italic | bullist numlist | link image media"
	});
	jQuery('.replybutton').hide();
	jQuery('.newreplygroup #delete').click(function (e) {
		jQuery('.replybutton').show();
		jQuery('.replyItemEdit').remove();
	});
	jQuery('.newreplygroup #save').click(function (e) {
		var annotation = {
			collectionId: self.endpoint.collection_id,
			contextId: self.endpoint.context_id,
			uri: self.window.canvasID,
			permissions: self.endpoint.catchOptions.permissions,
			user: self.endpoint.catchOptions.user,
			archived: false,
			rangePosition: {},
			ranges: [],
			tags: [],
			text: jQuery('.replyItemEdit .replytext').val(),
			parent: jQuery('.parentAnnotation .idAnnotation').html(),
			media: "comment",
		};

		self.endpoint.createCatchAnnotation(annotation);

		jQuery('.replybutton').show();
		jQuery('.replyItemEdit').remove();
	});
};

MiradorEndpointController.prototype.deleteAnnotation = function(annotation) {
	// given an annotation to be deleted, publish call to remove overlay from mirador
	// and send a signal to catch to delete
	mir.eventEmitter.publish('annotationDeleted.' + this.window.id, annotation.id.toString());
};

MiradorEndpointController.prototype.editAnnotation = function(annotation, button) {
	//given an annotation and the button (which contains location) update the item
	//in Mirador and send a request to catch to edit
	tinymce.init({ 
		selector:".parentAnnotation .body", 
		inline: true, 
		menubar: false,
		plugins: "image link media",
        statusbar: false,
        toolbar_items_size: 'small',
        toolbar: "bold italic | bullist numlist | link image media | removeformat"
	});
	jQuery('.parentAnnotation .editgroup').hide();
	jQuery('.parentAnnotation .savegroup').show();

	var currentBody = jQuery('.parentAnnotation .body').html();
	jQuery('.parentAnnotation .body').css({
		"outline": "1px solid white",
    	"margin-right": "10px",
    	"margin-bottom": "10px",
    	"padding": "3px",
    	"border": "2px solid gray",
	});
	var closeEditingMode = function(){
		jQuery('.parentAnnotation .body').css({
			"outline": "0px",
	    	"margin-right": "0px",
	    	"margin-bottom": "0px",
	    	"padding": "0px",
	    	"border": "0px",
		});
		jQuery('.parentAnnotation .editgroup').show();
		jQuery('.parentAnnotation .savegroup').hide();
		if (jQuery('.parentAnnotation .body').summernote !== undefined) {
			jQuery('.parentAnnotation .body').destroy();
		} else if(tinymce !== undefined){
			tinymce.remove();
		}
	};

	var self = this;
	jQuery('.parentAnnotation .savegroup #save').click(function(e) {
		var annotation = self.getAnnotationById(jQuery('.parentAnnotation .idAnnotation').html());
		annotation.text = jQuery('.parentAnnotation .body').html();
		var oaAnnotation = self.endpoint.getAnnotationInOA(annotation);
		mir.eventEmitter.publish('annotationUpdated.'+self.window.id, oaAnnotation);
		closeEditingMode();
	});

	jQuery('.parentAnnotation .savegroup #cancel').click(function(e) {
		closeEditingMode();
		jQuery('.parentAnnotation .body').html(currentBody);
	});

};

MiradorEndpointController.prototype.updateAnnotationInMasterList = function(annotation) {
	annotation.id = parseInt(annotation.id, 10);
	for (index in this.annotationsMasterList) {
		if (this.annotationsMasterList[index].id === annotation.id)
			this.annotationsMasterList[index] = annotation;
	}

};

MiradorEndpointController.prototype.loadRepliesForParentAnnotation = function(annotation_id, displayFunction) {
	// make a call to catch via mirador to get replies (should NOT draw them on screen)
	var anId = parseInt(annotation_id, 10);
	var self = this;

	var newLoadFromSearch = {
		parentid: anId,
		media: "comment",
		uri: self.endpoint.uri,
	};

	var onSuccess = function(data) {
		if (data === null) {
			data = {};
		}
		self.list_of_replies = data.rows || [];
		displayFunction(self.list_of_replies);
	};

	self.endpoint.search(newLoadFromSearch, onSuccess, function(){});
};

MiradorEndpointController.prototype.deleteReply = function(reply, callback) {
	// send a request to CATCH to destroy reply
	this.endpoint.deleteAnnotation(reply.id, callback);
};

MiradorEndpointController.prototype.queryDatabase = function(options, pagination, mediaType) {

	var setOptions = jQuery.extend({}, this.queryDefault, options);
	var self = this;
	var newOptions = {
		limit: -1,
		offset: 0,
		media: mediaType,
		userid: setOptions.user_id,
		username: setOptions.username,
		text: setOptions.text,
		tag: setOptions.tag,
		uri: self.window.canvasID,
	};

	var onSuccess = function(data){
		if (data === null) {
			data = {};
		}
		var annotations = data.rows || [];

		self.endpoint.annotationsListCatch = annotations;
		self.updateMasterList();
		self.window.annotationsList = [];

		annotations.forEach(function(annotation) {
			var oaAnnotation = self.endpoint.getAnnotationInOA(annotation);
			// trigger drawing here or once they're all loaded below
			self.window.annotationsList.push(oaAnnotation);
		});

		mir.eventEmitter.publish('ANNOTATIONS_LIST_UPDATED', {windowId: self.window.id, annotationsList: self.window.annotationsList});
		//mir.eventEmitter.publish('annotationListLoaded.' + self.window.id);
		mir.eventEmitter.publish('catchAnnotationsLoaded', annotations);
	}

	self.endpoint.search(newOptions, onSuccess, function(){});
};

MiradorEndpointController.prototype._clearAnnotator = function() {
	// Mirador handles clearing when necessary
};
