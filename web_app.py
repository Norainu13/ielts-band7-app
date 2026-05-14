#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os, random, datetime, subprocess, json, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, redirect, url_for, session
from ielts_app import READING_PASSAGES, LISTENING_SECTIONS, VOCAB_LIST, pct_to_band

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'ielts-band7-dev-secret')
app.jinja_env.globals.update(enumerate=enumerate)


# ── セッションベースの進捗管理（ユーザーごとにCookieに保存）──────────────────

def _prog():
    """現在のセッションの進捗データを返す（なければ初期化）"""
    if 'progress' not in session:
        session['progress'] = {
            'reading_scores': [],
            'listening_scores': [],
            'vocab_scores': [],
            'total_study_minutes': 0,
            'exercises_completed': 0,
            'streak_days': 0,
            'last_study_date': None,
        }
    return session['progress']


def _save_score(skill, score, max_score, exercise_name):
    p = _prog()
    entry = {
        'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        'exercise': exercise_name,
        'score': score,
        'max_score': max_score,
        'percentage': round(score / max_score * 100, 1) if max_score else 0,
    }
    key = f'{skill}_scores'
    p[key].append(entry)
    p[key] = p[key][-10:]  # 直近10件だけ保持（Cookie容量節約）
    p['exercises_completed'] += 1
    _update_streak(p)
    session.modified = True


def _add_time(minutes, p=None):
    if p is None:
        p = _prog()
    p['total_study_minutes'] += int(minutes)
    session.modified = True


def _update_streak(p):
    today = datetime.date.today().isoformat()
    last = p.get('last_study_date')
    if last is None:
        p['streak_days'] = 1
    elif last == today:
        pass
    else:
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        p['streak_days'] = p.get('streak_days', 0) + 1 if last == yesterday else 1
    p['last_study_date'] = today


def _estimate_band(skill):
    scores = _prog().get(f'{skill}_scores', [])
    if not scores:
        return None
    avg = sum(s['percentage'] for s in scores[-5:]) / min(len(scores), 5)
    return pct_to_band(avg)


# ── ヘルパー ───────────────────────────────────────────────────────────────────

def band_class(band):
    if band is None:
        return 'secondary'
    return 'success' if band >= 7.0 else ('warning' if band >= 6.0 else 'danger')


def band_label(band):
    return '未受験' if band is None else str(band)


# ── ルート ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    rb = _estimate_band('reading')
    lb = _estimate_band('listening')
    vb = _estimate_band('vocab')
    p = _prog()
    total_min = p.get('total_study_minutes', 0)
    h, m = divmod(total_min, 60)
    return render_template('index.html',
        rb=rb, lb=lb, vb=vb,
        band_class=band_class, band_label=band_label,
        hours=h, minutes=m,
        exercises=p.get('exercises_completed', 0),
        streak=p.get('streak_days', 0))


# ── Reading ──────────────────────────────────────────────────────────────────

@app.route('/reading')
def reading_list():
    return render_template('reading_list.html', passages=READING_PASSAGES)


@app.route('/reading/<int:pid>', methods=['GET', 'POST'])
def reading_detail(pid):
    passage = next((p for p in READING_PASSAGES if p['id'] == pid), None)
    if not passage:
        return redirect(url_for('reading_list'))
    if request.method == 'POST':
        return _process_exercise(passage['questions'], passage['title'],
                                 'reading', passage['band7_tips'],
                                 url_for('reading_list'), time_minutes=20)
    return render_template('exercise.html', mode='reading', content=passage)


# ── Listening ─────────────────────────────────────────────────────────────────

@app.route('/listening')
def listening_list():
    return render_template('listening_list.html', sections=LISTENING_SECTIONS)


@app.route('/listening/<int:sid>', methods=['GET', 'POST'])
def listening_detail(sid):
    section = next((s for s in LISTENING_SECTIONS if s['id'] == sid), None)
    if not section:
        return redirect(url_for('listening_list'))
    if request.method == 'POST':
        return _process_exercise(section['questions'], section['title'],
                                 'listening', section['band7_tips'],
                                 url_for('listening_list'), time_minutes=10)
    transcript_lines = _parse_transcript(section['transcript'])
    return render_template('exercise.html', mode='listening', content=section,
                           transcript_lines=transcript_lines)


def _parse_transcript(raw):
    lines = []
    for line in raw.split('\n'):
        if ':' in line:
            parts = line.split(':', 1)
            if parts[0].isupper() and parts[0].strip():
                lines.append({'speaker': parts[0].strip(), 'text': parts[1].strip()})
                continue
        lines.append({'speaker': None, 'text': line})
    return lines


def _process_exercise(question_sets, title, skill, tips, back_url, time_minutes):
    total_score = 0
    total_max = 0
    results = []

    for qi, q_set in enumerate(question_sets):
        qtype = q_set['type']
        set_score = 0
        set_items = []

        if qtype in ('true_false_ng', 'multiple_choice', 'short_answer', 'fill_blank'):
            for ii, item in enumerate(q_set['items']):
                user_ans = request.form.get(f'q_{qi}_{ii}', '').strip()
                if qtype == 'true_false_ng':
                    correct = user_ans.upper() in item['alt'] or user_ans.upper() == item['answer']
                elif qtype == 'multiple_choice':
                    correct = user_ans.upper() == item['answer']
                else:
                    correct = any(kw.lower() in user_ans.lower() for kw in item['keywords'])
                if correct:
                    set_score += 1
                set_items.append({
                    'q': item['q'],
                    'user_ans': user_ans,
                    'correct_ans': item['answer'],
                    'correct': correct,
                    'explanation': item['explanation'],
                    'options': item.get('options', []),
                })
            total_max += len(q_set['items'])

        elif qtype == 'matching':
            item = q_set['items'][0]
            for concept_letter, correct_num in item['answers'].items():
                user_ans = request.form.get(f'match_{qi}_0_{concept_letter}', '').strip()
                correct = user_ans == correct_num
                if correct:
                    set_score += 1
                concept_text = next((c for c in item['concepts'] if c.startswith(concept_letter + '.')), concept_letter)
                desc_text = next((d for d in item['descriptions'] if d.startswith(correct_num + '.')), correct_num)
                set_items.append({
                    'q': concept_text,
                    'user_ans': user_ans,
                    'correct_ans': correct_num,
                    'correct': correct,
                    'explanation': f"{concept_text} → {desc_text}",
                    'options': [],
                })
            total_max += len(item['answers'])

        total_score += set_score
        results.append({
            'label': q_set['label'],
            'type': qtype,
            'score': set_score,
            'max': len(set_items),
            'items': set_items,
        })

    pct = round(total_score / total_max * 100, 1) if total_max else 0
    band = pct_to_band(pct)
    _save_score(skill, total_score, total_max, title)
    _add_time(time_minutes)

    return render_template('result.html',
        title=title, skill=skill,
        total_score=total_score, total_max=total_max, pct=pct,
        band=band, band_cls=band_class(band),
        results=results, tips=tips, back_url=back_url)


# ── Vocabulary ────────────────────────────────────────────────────────────────

@app.route('/vocab')
def vocab_menu():
    return render_template('vocab_menu.html', word_count=len(VOCAB_LIST))


@app.route('/vocab/list')
def vocab_list():
    return render_template('vocab_list.html', words=VOCAB_LIST)


@app.route('/vocab/flashcard')
def vocab_flashcard():
    words = random.sample(VOCAB_LIST, min(10, len(VOCAB_LIST)))
    return render_template('vocab_flashcard.html', words=words)


@app.route('/vocab/quiz', methods=['GET', 'POST'])
def vocab_quiz():
    if request.method == 'POST':
        answers = session.get('vocab_quiz', [])
        score = 0
        results = []
        for i, entry in enumerate(answers):
            user_ans = request.form.get(f'q_{i}', '').strip().upper()
            correct = user_ans == entry['correct']
            if correct:
                score += 1
            results.append({
                'word': entry['word'],
                'user_ans': user_ans,
                'correct_ans': entry['correct'],
                'correct': correct,
                'definition': entry['def'],
                'synonyms': entry['syn'],
                'options': entry['options'],
            })
        pct = round(score / len(answers) * 100, 1) if answers else 0
        band = pct_to_band(pct)
        _save_score('vocab', score, len(answers), '語彙4択クイズ')
        _add_time(8)
        return render_template('vocab_result.html',
            score=score, total=len(answers), pct=pct,
            band=band, band_cls=band_class(band), results=results)

    words = random.sample(VOCAB_LIST, min(10, len(VOCAB_LIST)))
    questions = []
    quiz_session = []
    for w in words:
        distractors = random.sample([v for v in VOCAB_LIST if v['word'] != w['word']], 3)
        opts = [w] + distractors
        random.shuffle(opts)
        correct_letter = chr(65 + next(i for i, o in enumerate(opts) if o['word'] == w['word']))
        options = [(chr(65 + i), o['def']) for i, o in enumerate(opts)]
        questions.append({'word': w['word'], 'ex': w['ex'], 'options': options})
        quiz_session.append({
            'word': w['word'], 'correct': correct_letter,
            'def': w['def'], 'syn': w['syn'], 'options': options,
        })
    session['vocab_quiz'] = quiz_session
    return render_template('vocab_quiz.html', questions=questions)


# ── Dashboard & Guide ─────────────────────────────────────────────────────────

@app.route('/dashboard')
def dashboard():
    p = _prog()
    total_min = p.get('total_study_minutes', 0)
    h, m = divmod(total_min, 60)
    skills = {}
    for key, label in [('reading', 'リーディング'), ('listening', 'リスニング'), ('vocab', '語彙')]:
        scores = p.get(f'{key}_scores', [])
        band = _estimate_band(key)
        skills[key] = {
            'label': label, 'scores': scores,
            'band': band, 'band_cls': band_class(band),
            'count': len(scores),
            'last': scores[-1] if scores else None,
        }
    return render_template('dashboard.html',
        hours=h, minutes=m,
        exercises=p.get('exercises_completed', 0),
        streak=p.get('streak_days', 0),
        skills=skills, band_label=band_label)


@app.route('/guide')
def guide():
    sections = [
        ('📖 READING の攻略', [
            'スキャニング: キーワードを文中で素早く探す技術を磨く',
            'スキミング: 段落全体の意味を速く把握する (15秒/段落)',
            'TRUE/FALSE/NG: 「書かれていないこと」= NOT GIVEN。自分の知識を使わない',
            'Matching Headings: パラグラフのメインアイデアを掴む練習',
            '時間配分: 20分/パッセージ。難問はスキップして後で戻る',
            '語彙力: Paraphrase (言い換え) を見抜く能力が必要',
        ]),
        ('🎧 LISTENING の攻略', [
            '先読み (prediction): 問題を先に読み、何を聞くか予測する',
            '数字・固有名詞: 電話番号・日付・金額は特に正確に',
            '話者の意見: 同意/反論/補足 を区別する',
            'スペル: 固有名詞のスペルミスは不正解になる',
            'Section 3&4: 学術語彙に慣れておく',
        ]),
        ('✍️ WRITING の攻略 (参考)', [
            'Task 1: データを客観的に記述。目立つ特徴を必ず含める',
            'Task 2: Intro→Body×2→Conclusionの4段落構成',
            '語彙の多様性: 同じ単語を繰り返さず、同義語を使う',
            '文法の正確性: 複文・関係代名詞・受動態を適切に使う',
        ]),
        ('🗣️ SPEAKING の攻略 (参考)', [
            '流暢さ: 沈黙を避け、つなぎ言葉 (well, actually) を活用',
            '語彙: 質問と同じ単語を避け、paraphrase する',
            'Part 2: 2分間話せるよう、アイデアを素早くまとめる練習',
            '発音: 正確さより流暢さと自然なリズムを意識する',
        ]),
        ('📅 学習スケジュール (週5日想定)', [
            '月: リーディング練習 (1パッセージ + 語彙30分)',
            '火: リスニング練習 (2セクション + 語彙30分)',
            '水: ライティング練習 (Task 2 エッセイ1本)',
            '木: リーディング練習 (1パッセージ) + スピーキング練習',
            '金: 弱点克服 + 語彙復習 + 模擬試験形式',
        ]),
    ]
    targets = [
        'リーディング: 30問中 23問以上正解 (76%+)',
        'リスニング  : 40問中 30問以上正解 (75%+)',
        'ライティング: Task 2 で論理的・語彙豊かなエッセイ',
        'スピーキング: 流暢・正確・語彙豊かな2分間スピーチ',
    ]
    return render_template('guide.html', sections=sections, targets=targets)


# ── Deploy ───────────────────────────────────────────────────────────────────

DEPLOY_DIR = os.path.dirname(os.path.abspath(__file__))


def _github_api(path, token, data=None):
    url = f'https://api.github.com{path}'
    headers = {
        'Authorization': f'token {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.github.v3+json',
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read()), resp.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code


def _run(cmd, cwd=None, env=None):
    result = subprocess.run(
        cmd, shell=True, cwd=cwd or DEPLOY_DIR,
        capture_output=True, text=True, env=env
    )
    return result.returncode == 0, result.stdout + result.stderr


@app.route('/deploy', methods=['GET', 'POST'])
def deploy():
    if request.method == 'GET':
        return render_template('deploy.html', step=None)

    token = request.form.get('token', '').strip()
    repo_name = request.form.get('repo_name', 'ielts-band7-app').strip()

    logs = []

    # 1. トークン確認・ユーザー名取得
    user_data, status = _github_api('/user', token)
    if status != 200:
        return render_template('deploy.html', error='トークンが無効です。再確認してください。')
    username = user_data['login']
    logs.append(f'✓ GitHubユーザー確認: {username}')

    # 2. リポジトリ作成（既存なら無視）
    repo_data, status = _github_api('/user/repos', token, {
        'name': repo_name,
        'description': 'IELTS Band 7 Master - 4技能学習Webアプリ',
        'private': False,
    })
    if status == 201:
        logs.append(f'✓ リポジトリ作成: github.com/{username}/{repo_name}')
    elif status == 422:
        logs.append(f'✓ 既存リポジトリを使用: github.com/{username}/{repo_name}')
    else:
        msg = repo_data.get('message', 'Unknown error')
        return render_template('deploy.html', error=f'リポジトリ作成失敗: {msg}', logs=logs)

    push_url = f'https://{token}@github.com/{username}/{repo_name}.git'
    repo_url = f'https://github.com/{username}/{repo_name}'

    # 3. Git 初期化 & プッシュ
    git_env = {**os.environ, 'GIT_TERMINAL_PROMPT': '0'}

    if not os.path.isdir(os.path.join(DEPLOY_DIR, '.git')):
        _run('git init -q && git branch -M main', env=git_env)

    _run('git config user.email "deploy@ielts-app.local"')
    _run('git config user.name "IELTS Deploy"')

    files = 'web_app.py ielts_app.py templates/ requirements.txt Procfile render.yaml .gitignore'
    ok, out = _run(f'git add {files}')
    _run('git commit -q -m "Deploy IELTS Band 7 Master" --allow-empty')

    _run('git remote remove origin 2>/dev/null; true')
    _run(f'git remote add origin "{push_url}"')
    ok, out = _run(f'git push -q -u origin main --force', env=git_env)
    if not ok:
        return render_template('deploy.html', error=f'プッシュ失敗: {out}', logs=logs)
    logs.append('✓ GitHubへプッシュ完了')

    render_url = f'https://render.com/deploy?repo={repo_url}'
    return render_template('deploy.html', success=True, logs=logs,
                           repo_url=repo_url, render_url=render_url)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
