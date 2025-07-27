from flask import Flask, render_template, request, redirect, url_for
import random
import json
import datetime
import os

app = Flask(__name__)

# Load all questions
with open('questions.json') as f:
    all_questions = json.load(f)

# File paths
leaderboard_file = 'leaderboard.json'
reset_file = 'last_reset.txt'

# Ensure reset timestamp file exists
if not os.path.exists(reset_file):
    with open(reset_file, 'w') as f:
        f.write(str(datetime.datetime.now()))

# Leaderboard auto-reset every 7 days
def reset_leaderboard_if_needed():
    with open(reset_file, 'r') as f:
        last_reset = datetime.datetime.fromisoformat(f.read().strip())
    now = datetime.datetime.now()
    if (now - last_reset).days >= 7:
        with open(leaderboard_file, 'w') as f:
            json.dump([], f)
        with open(reset_file, 'w') as f:
            f.write(str(now))

@app.route('/')
def index():
    reset_leaderboard_if_needed()
    try:
        with open(leaderboard_file, 'r') as f:
            leaderboard = json.load(f)
    except FileNotFoundError:
        leaderboard = []

    sorted_board = sorted(leaderboard, key=lambda x: x['score'], reverse=True)[:20]
    return render_template('index.html', leaderboard=sorted_board)

@app.route('/quiz', methods=['POST'])
def quiz():
    name = request.form['name']
    category = request.form['category']
    questions_pool = all_questions.get(category, [])
    selected_questions = random.sample(questions_pool, 10)
    return render_template('quiz.html', name=name, category=category, questions=selected_questions)

@app.route('/results', methods=['POST'])
def results():
    name = request.form['name']
    category = request.form['category']
    score = 0
    results = []

    for i in range(10):
        question = request.form.get(f'q{i}_question')
        selected = request.form.get(f'q{i}_answer')
        correct = request.form.get(f'q{i}_correct')
        is_correct = selected == correct
        results.append({
            'question': question,
            'selected': selected,
            'correct': correct,
            'is_correct': is_correct
        })
        if is_correct:
            score += 5
        else:
            score -= 2

    # Load and update leaderboard
    try:
        with open(leaderboard_file, 'r') as f:
            leaderboard = json.load(f)
    except FileNotFoundError:
        leaderboard = []

    leaderboard.append({
        'name': name,
        'score': score,
        'category': category
    })

    with open(leaderboard_file, 'w') as f:
        json.dump(leaderboard, f, indent=2)

    return render_template('results.html', name=name, score=score, results=results)

@app.route('/leaderboard')
def leaderboard_page():
    reset_leaderboard_if_needed()
    try:
        with open(leaderboard_file, 'r') as f:
            leaderboard = json.load(f)
    except FileNotFoundError:
        leaderboard = []

    sorted_board = sorted(leaderboard, key=lambda x: x['score'], reverse=True)[:20]
    return render_template('leaderboard.html', leaderboard=sorted_board)

if __name__== '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)