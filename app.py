from flask import Flask, render_template, request

app = Flask(__name__)   # intialize the flask application

# @app.route('/', methods=['GET', 'POST'])
# def index():

if __name__ == '__main__':
    app.run(debug=True)
  