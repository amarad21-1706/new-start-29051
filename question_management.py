
from flask import Blueprint, request, render_template
from app.models.user import Question
from flask.views import MethodView

bp = Blueprint('question_management', __name__)


def get_entity_by_id(model, entity_id):
    # Retrieve the question from the database based on the provided ID
    entity = model.query.get(entity_id)
    # Check if the ent was found
    if not entity:
        # Raise an exception if the question was not found
        raise EntityNotFoundError
    return entity


def get_question_by_id(question_id):
    # Retrieve the question from the database based on the provided ID
    question = Question.query.get(question_id)
    # Check if the question was found
    if not question:
        # Raise an exception if the question was not found
        raise QuestionNotFoundError
    return question


# Define your CRUD views for the Question model
class QuestionReadView(MethodView):
    def get(self):
        # Replace this with your logic to retrieve Question data
        companiess = get_question_data()
        return render_template('crud_read_template.html', model_name='Question', fields=Question.__table__.columns, items=companies)

class QuestionRetrieveView(MethodView):
    def get(self, item_id):
        # Replace this with your logic to retrieve a specific Question by item_id
        question = get_question_by_id(item_id)
        #ent = get_entity_by_id(Question, item_id)
        #print('generic ENTITY', ent)
        print('specific Question', question)
        return render_template('crud_retrieve_template.html', model_name='Question', fields=Question.__table__.columns, item=question, question=question)

class QuestionCreateView(MethodView):
    def get(self):
        return render_template('crud_create_template.html', model_name='Question', fields=Question.__table__.columns)

    def post(self):
        # Replace this with your logic to create a new Question
        create_question(request.form)
        return redirect(url_for('model_question.read'))


class QuestionUpdateView(MethodView):
    def get(self, item_id):
        # Replace this with your logic to retrieve a specific Question by item_id
        question = get_question_by_id(item_id)
        return render_template('crud_update_template.html', model_name='Question', fields=Question.__table__.columns, item=question)

    def post(self, item_id):
        # Replace this with your logic to update a specific Question by item_id
        update_question(item_id, request.form)
        return redirect(url_for('model_question.read'))


class QuestionDeleteView(MethodView):
    def post(self, item_id):
        # Redirect to the confirmation page
        return redirect(url_for('model_question_delete', model_name='Question', item_id=item_id))

