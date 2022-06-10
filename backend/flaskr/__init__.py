import os
from flask import Flask, request, abort, json, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from numpy import result_type
from scipy.fftpack import diff

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate(request, data):
    """
        Pagination function to limit the page to a maximum
        Of 10 questions per page
    """
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    formatted_data = [item.format() for item in data]

    return formatted_data[start: end]

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})


    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    Status = Done.
   """

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    Status = Done
    """


    @app.route('/categories')
    def category():
        # Fetch all categories from the categories table
        all_categories = Category.query.all()
        
        # Store each category item in categories dict to return type as json
        categories = {
            category.id: category.type for category in all_categories}

        return jsonify({
            'success': True,
            "categories": categories
        })

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    Status = Done
    """


    @app.route('/questions')
    def question():
        # Fetch all the categories
        cat = Category.query.all()
        categories = {
            category.id: category.type for category in cat
            }
        
        # Fetch all thr questions and limit them to 10 per page
        questions = Question.query.all()
        paginated_questions = paginate(request, questions)

        if not len(paginated_questions):
            abort(404)
        
        
        return jsonify({
            'success': True,
            'questions': paginated_questions,
            'total_questions': len(paginated_questions),
            'categories': categories
        })
            
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    Status = Done
    """

    """
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete(question_id):
        # Fetch the question using the question_id
        question = Question.query.get(question_id)
        
        if not question:
            abort(404)

        else:
            # Use the delete function in the model.py to delete the question
            # And erase the data from the database by commiting the change
            question.delete()
            return jsonify({
                "success": True,
                "deleted": question.id
            })
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.
    Status = Done

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """


       
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    
    Status = Done, added the search and create function together

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """


    @app.route("/questions", methods=["POST"])
    def add_question():
        '''
          Endpoint to posts a new question and search for 
          previous questions based on a search term.
        '''
        try:
            data = request.get_json()
            
            # Get the search phrase from the client
            searchTerm = data.get("searchTerm", None)

            # Iterate through the questions table to find similar phrase in any question
            if searchTerm is not None:
                questions = Question.query.filter(
                    Question.question.ilike("%{}%".format(searchTerm))
                ).all()
                
                # Format the questions using the format function in models.py
                formatted_question = [question.format()
                                       for question in questions]

                # Return questions with similar phrase as the search term
                return jsonify({
                    'success': True,
                    "questions": formatted_question,
                    "totalQuestions": len(questions),
                    "currentCategory": None
                })
            else:
                # This handles the POST request to post a new question
                # By getting the question posted in the form
                question = data["question"]
                answer = data["answer"]
                difficulty = int(data["difficulty"])
                category = int(data["category"])

                # This creates a new question object ready to be added to the db
                question = Question(
                    question=question,
                    answer=answer,
                    difficulty=difficulty,
                    category=category,
                )

                # This calls the insert function in the model.py which adds and commits the
                # Newly created object to the database
                question.insert()

                return jsonify({
                    "added": question.id,
                    "success": True,
                })

        except Exception:
            abort(400)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.
    
    Status = Done

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """



    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def question_by_category(category_id):
        """
            Endpoint to get questions according to categories
        """
        # Query the questions table and filter by category
        data = Question.query.filter_by(category=category_id).all()
        
        # Format the data using the format function in models.py
        formatted_questions = [question.format() for question in data]

        return jsonify({
            "questions": formatted_questions,
            "totalQuestions": len(data),
            "Category": None
        })
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    Status = Done

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """



    @app.route("/quizzes", methods=["POST"])
    def get_question_for_quiz():
        data = request.json
        try:
            category = data['quiz_category']['id']
        except:
            abort(400)

        if category == 0:
            # Get questions from all categories
            questions = Question.query.all()
        else:
            # Get questions for only one category
            questions = Question.query.filter_by(category=str(category)).all()

        # # Format the questions using the format function in models.py
        questions = [question.format() for question in questions]  

        # Get the previously asked questions
        try:
            prev_question = data['previous_questions']
        except:
            abort(400)
        
        # Sort out and append questions not previously asked
        sorted_questions = []
        for item in questions:
            if item['id'] not in prev_question:
                sorted_questions.append(item)

        # Return no new question if player has exhausted the sorted questions list.
        if len(sorted_questions) == 0:
            return jsonify({
                'success': True
            })

        # Else, return a random question from the sorted list
        question = random.choice(sorted_questions)
        
        return jsonify({
            'success': True,
            'question': question
        })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    Stauus = Done


    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """



    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "Resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "Unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "Bad request"}), 400

    @app.errorhandler(405)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 405, "message": "Method not allowed"}),
            405,
        )


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    return app

