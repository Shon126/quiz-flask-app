from flask import Flask, render_template, request, redirect, url_for, send_file
import random
import json
import os

from db import init_db, add_score, get_top_20

app = Flask(__name__)
init_db()

# Load questions once
with open('questions.json') as f:
    all_questions = json.load(f)

@app.route('/')
def index():
    leaderboard = get_top_20()
    return render_template('index.html', leaderboard=[
        {"name": name, "score": score, "category": category}
        for name, score, category in leaderboard
    ])

@app.route('/quiz', methods=['POST'])
def quiz():
    name = request.form['name']
    category = request.form['category']
    questions_pool = all_questions.get(category, [])
    selected_questions = random.sample(questions_pool, 10)

    # Pass name & category back to results via form
    return render_template('quiz.html', name=name, category=category, questions=selected_questions)

@app.route('/results', methods=['POST'])
def results():
    name = request.form.get('name')
    category = request.form.get('category')
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

        score += 5 if is_correct else -2

    score = max(score, 0)  # Don't allow negative scores
    try:
        add_score(name, score, category)
    except Exception as e:
        print(f"Error saving score: {e}")

    return render_template('results.html', name=name, score=score, results=results)

@app.route('/leaderboard')
def leaderboard_page():
    leaderboard = get_top_20()
    return render_template('leaderboard.html', leaderboard=[
        {"name": name, "score": score, "category": category}
        for name, score, category in leaderboard
    ])

@app.route('/download-db')
def download_db():
    return send_file('leaderboard.db', as_attachment=True)

if __name__== '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)