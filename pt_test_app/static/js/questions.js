var QuestionModel = Backbone.Model.extend({
    urlRoot: window.URLs.QUESTION_URL,

    defaults: {
        text: '',
        choices: [{text: "", checked: false}, {text: "", checked: false}]
    },

    validate: function (attrs, options) {
        var errors = {};
        if ( !$.trim(attrs.text) ) {
            errors.text = ['Text cannot be empty']
        }
        return _.isEmpty(errors) ? false : errors;
    }

});

var QuestionCollection = Backbone.Collection.extend({
    model: QuestionModel
});

var QuestionView = Backbone.View.extend({

    el: $('#question-edit-area'),

    events: {
        'click #save-btn': 'clickSaveButton',
        'click #add-answer': 'addAnswer',
        'click .delete': 'deleteChoice'
    },

    initialize: function (conf) {
        this.listenTo(this.model, 'invalid', this.render);
        this.listenTo(this.model, 'request', this.eventSyncStarted);
        this.listenTo(this.model, 'error', this.eventSyncFailed);
        this.listenTo(this.model, 'sync', this.eventSyncCompleted);
        this.template = _.template($('#question-template').html());
        this.serverErrors = {};
        this.UI = {}; // initialized in first render
    },

    reinitializeUI: function () {
        this.UI = {
            $text: this.$el.find('.text textarea'),
            $choices: this.$el.find('.choices .row'),
        };
    },
    
    getElement: function (path) {
        return this.$el.find(path)
    },

    clickSaveButton: function (e) {
        var choices = [];
        _.each(this.getElement('.choices .row'), function (choice) {
            $choice = $(choice);
            var text = $choice.find('input[type=text]').val();
            var is_answer = $choice.find('input[type=checkbox]').prop('checked');
            choices.push({text: text, is_answer: is_answer});
            console.log('choices:' + choices)
        });
        this.model.set({
            text: this.UI.$text.val(),
            choices: choices
        });
        this.model.save(null, {
            beforeSend: function (xhr) {
                xhr.setRequestHeader('X-CSRFToken', Cookies.get("csrftoken"));
            }
        })
    },
    
    addAnswer: function (e) {        
        $(
            '<div class="row">' +
            '<div class="col-lg-9"><input class="form-control" type="text" value=""></div>' + 
            '<div class="col-lg-1"><input class="form-control" type="checkbox"></div>' + 
            '<div class="col-lg-1"><button class="delete">X</button></div>' +
            '</div>'
        ).appendTo(this.$el.find('.choices'))
    },
    
    deleteChoice: function (e) {
        $(e.currentTarget).closest('.row').remove()
    },

    toggleSpinner: function (enable) {
        // TODO
    },

    eventSyncStarted: function (e) {
        this.serverErrors = {};
        this.toggleSpinner(true)
    },

    eventSyncFailed: function (model, response, options) {
        this.toggleSpinner(false);
        this.serverErrors = response.responseJSON;
        this.render();
    },

    eventSyncCompleted: function (e) {
        this.toggleSpinner(false);
        this.collection.set(this.model.clone(), {remove: false})
    },

    render: function () {
        console.log(this.model.attributes);
        this.$el.html(this.template({
            model: this.model,
            serverErrors: this.serverErrors
        }));
        this.reinitializeUI()
    },

    createNewQuestion: function () {
        console.log('here');
        this.model.clear({silent: true});
        this.model.set(this.model.defaults);
        this.render()
    }

});

var ShortQuestionView = Backbone.View.extend({
    tagName: 'div',
    className: 'question-short-area',

    events: {
        'click': 'editQuestion'
    },

    initialize: function (conf) {
        this.template = _.template($('#question-short').html());
    },

    render: function () {
        return this.$el.html(this.template({model: this.model}));
    },

    editQuestion: function () {
        viewQuestion.model.set(this.model.attributes);
        viewQuestion.render();
    }
});

var QuestionsView = Backbone.View.extend({
    el: $('#questions-list'),

    initialize: function (conf) {
        this.listenTo(this.collection, 'add', this.render);
        this.listenTo(this.collection, 'change', this.render);
    },

    render: function () {
        this.$el.html('');
        this.collection.each(_.bind(function (modelQuestion) {
            this.$el.append((new ShortQuestionView({model: modelQuestion})).render());
        }, this));
        return this;
    }
});