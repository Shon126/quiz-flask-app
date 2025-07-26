from flask import Flask, render_template, request, redirect, url_for
import random
import json
import datetime
import os

app = Flask(__name__)

# Load questions
with open('questions.json') as f:
    all_questions = json.load(f)

# Load or initialize leaderboard
leaderboard_file = 'leaderboard.json'
if os.path.exists(leaderboard_file):
    with open(leaderboard_file) as f:
        leaderboard = json.load(f)
else:
    leaderboard = []

# Last reset tracking
reset_file = 'last_reset.txt'
if not os.path.exists(reset_file):
    with open(reset_file, 'w') as f:
        f.write(str(datetime.datetime.now()))

def reset_leaderboard_if_needed():
    with open(reset_file, 'r') as f:
        last_reset = datetime.datetime.fromisoformat(f.read().strip())
    now = datetime.datetime.now()
    if (now - last_reset).days >= 7:
        global leaderboard
        leaderboard = []
        with open(leaderboard_file, 'w') as f:
            json.dump(leaderboard, f)
        with open(reset_file, 'w') as f:
            f.write(str(now))

@app.route('/')
def index():
    reset_leaderboard_if_needed()
    sorted_board = sorted(leaderboard, key=lambda x: x['score'], reverse=True)
    return render_template('index.html', leaderboard=sorted_board)

@app.route('/quiz', methods=['POST'])
def quiz():
    name = request.form['name']
    category = request.form['category']
    questions_pool = all_questions.get(category, [])
    selected_questions = random.sample(questions_pool, 10)
    return render_template('quiz.html', name=name, category=category, questions=selected_questions)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    category = request.form['category']
    score = 0
    for i in range(10):
        selected = request.form.get(f'q{i}_answer')
        correct = request.form.get(f'q{i}_correct')
        if selected == correct:
            score += 5
        else:
            score -= 2
    leaderboard.append({'name': name, 'score': score, 'category': category})
    with open(leaderboard_file, 'w') as f:
        json.dump(leaderboard, f)
    return redirect(url_for('leaderboard_page'))

@app.route('/leaderboard')
def leaderboard_page():
    reset_leaderboard_if_needed()
    sorted_board = sorted(leaderboard, key=lambda x: x['score'], reverse=True)
    return render_template('leaderboard.html', leaderboard=sorted_board)

if __name__== '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)