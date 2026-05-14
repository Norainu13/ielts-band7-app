#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════╗
║    IELTS Band 7 Master - 完全学習アプリ       ║
║    Focus: Reading & Listening                ║
║    Target: Band 7+                           ║
╚══════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
import random
import datetime
import textwrap

# ─────────────────────────────────────────────
# ANSI カラーコード
# ─────────────────────────────────────────────
class C:
    RESET    = '\033[0m'
    BOLD     = '\033[1m'
    DIM      = '\033[2m'
    RED      = '\033[91m'
    GREEN    = '\033[92m'
    YELLOW   = '\033[93m'
    BLUE     = '\033[94m'
    MAGENTA  = '\033[95m'
    CYAN     = '\033[96m'
    WHITE    = '\033[97m'

    @staticmethod
    def bold(t):    return f'\033[1m{t}\033[0m'
    @staticmethod
    def green(t):   return f'\033[92m{t}\033[0m'
    @staticmethod
    def red(t):     return f'\033[91m{t}\033[0m'
    @staticmethod
    def yellow(t):  return f'\033[93m{t}\033[0m'
    @staticmethod
    def blue(t):    return f'\033[94m{t}\033[0m'
    @staticmethod
    def cyan(t):    return f'\033[96m{t}\033[0m'
    @staticmethod
    def magenta(t): return f'\033[95m{t}\033[0m'
    @staticmethod
    def dim(t):     return f'\033[2m{t}\033[0m'


# ─────────────────────────────────────────────
# ユーティリティ関数
# ─────────────────────────────────────────────
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause(msg="Enterキーを押して続ける..."):
    input(f"\n{C.dim(msg)}")

def divider(char='─', width=55):
    print(C.dim(char * width))

def header(title, icon="📚"):
    print(f"\n{C.BOLD}{C.CYAN}{'═' * 55}")
    print(f"  {icon}  {title}")
    print(f"{'═' * 55}{C.RESET}")

def wrap_print(text, width=70, indent=2):
    """テキストを折り返して表示"""
    lines = text.split('\n')
    for line in lines:
        if line.strip() == '':
            print()
        else:
            wrapped = textwrap.fill(line, width=width, initial_indent=' ' * indent,
                                    subsequent_indent=' ' * indent)
            print(wrapped)

def band_color(band):
    if band >= 7.0:   return C.GREEN
    elif band >= 6.0: return C.YELLOW
    else:             return C.RED

def pct_to_band(pct):
    if pct >= 95: return 9.0
    elif pct >= 90: return 8.5
    elif pct >= 85: return 8.0
    elif pct >= 80: return 7.5
    elif pct >= 73: return 7.0
    elif pct >= 65: return 6.5
    elif pct >= 57: return 6.0
    elif pct >= 50: return 5.5
    elif pct >= 43: return 5.0
    else: return 4.5


# ─────────────────────────────────────────────
# 進捗トラッカー
# ─────────────────────────────────────────────
PROGRESS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'progress.json')

class ProgressTracker:
    def __init__(self):
        self.data = self._load()

    def _load(self):
        if os.path.exists(PROGRESS_FILE):
            try:
                with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            'reading_scores': [],
            'listening_scores': [],
            'vocab_scores': [],
            'total_study_minutes': 0,
            'exercises_completed': 0,
            'streak_days': 0,
            'last_study_date': None
        }

    def save(self):
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def update_streak(self):
        today = datetime.date.today().isoformat()
        last = self.data.get('last_study_date')
        if last is None:
            self.data['streak_days'] = 1
        elif last == today:
            pass  # 今日はすでに記録済み
        else:
            yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
            if last == yesterday:
                self.data['streak_days'] = self.data.get('streak_days', 0) + 1
            else:
                self.data['streak_days'] = 1
        self.data['last_study_date'] = today
        self.save()

    def add_score(self, skill, score, max_score, exercise_name):
        entry = {
            'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            'exercise': exercise_name,
            'score': score,
            'max_score': max_score,
            'percentage': round(score / max_score * 100, 1) if max_score else 0
        }
        self.data[f'{skill}_scores'].append(entry)
        self.data['exercises_completed'] += 1
        self.save()

    def add_time(self, minutes):
        self.data['total_study_minutes'] += int(minutes)
        self.update_streak()
        self.save()

    def estimate_band(self, skill):
        scores = self.data.get(f'{skill}_scores', [])
        if not scores:
            return None
        recent = scores[-5:]
        avg = sum(s['percentage'] for s in recent) / len(recent)
        return pct_to_band(avg)

    def show_dashboard(self):
        clear()
        header("学習ダッシュボード", "📊")

        total_min = self.data.get('total_study_minutes', 0)
        h, m = divmod(total_min, 60)
        streak = self.data.get('streak_days', 0)

        print(f"\n  {C.yellow('総学習時間:')}  {C.bold(f'{h}時間{m}分')}")
        print(f"  {C.yellow('完了した演習:')} {C.bold(str(self.data.get('exercises_completed', 0)))}回")
        print(f"  {C.yellow('連続学習日数:')} {C.bold(str(streak))}日 🔥")

        skills = [
            ('reading',   'リーディング', '📖'),
            ('listening', 'リスニング',   '🎧'),
            ('vocab',     '語彙',         '📝'),
        ]

        for skill, label, icon in skills:
            scores = self.data.get(f'{skill}_scores', [])
            print(f"\n  {icon} {C.blue(C.bold(label))}")
            divider()
            if scores:
                last = scores[-1]
                band = self.estimate_band(skill)
                print(f"    最新スコア : {last['score']}/{last['max_score']} ({last['percentage']}%)")
                print(f"    演習回数   : {len(scores)}回")
                if band:
                    bc = band_color(band)
                    print(f"    推定バンド : {bc}{C.bold(str(band))}{C.RESET}")
                    if band < 7.0:
                        recent_pct = sum(s['percentage'] for s in scores[-5:]) / min(len(scores), 5)
                        target_pct = 73.0
                        diff = max(0, target_pct - recent_pct)
                        print(f"    Band 7まで : あと正解率 {C.yellow(f'+{diff:.0f}%')} が必要")
                    else:
                        print(f"    {C.green('✓ Band 7 達成圏内です！')}")
            else:
                print(f"    {C.dim('まだ演習を行っていません')}")

        pause()


# ─────────────────────────────────────────────
# ─── リーディングデータ ───────────────────────
# ─────────────────────────────────────────────
READING_PASSAGES = [
    {
        'id': 1,
        'title': 'Passage 1: The Future of Renewable Energy',
        'level': 'Academic',
        'time_limit': 20,
        'text': (
            "Renewable energy sources have undergone a remarkable transformation over the past two decades. "
            "Once considered an expensive and unreliable alternative to fossil fuels, solar and wind power "
            "have now emerged as cost-competitive options in many parts of the world. The International Energy "
            "Agency (IEA) reports that in 2023, renewable energy accounted for approximately 30% of global "
            "electricity generation, a figure that is expected to rise significantly by 2030.\n\n"
            "The driving forces behind this transition are both technological and economic. The cost of solar "
            "photovoltaic (PV) panels has fallen by more than 90% since 2010, largely due to improvements in "
            "manufacturing processes and economies of scale. Similarly, wind turbine technology has advanced "
            "considerably, with modern offshore turbines capable of generating up to 15 megawatts of power—"
            "enough to supply thousands of homes. These technological breakthroughs have made renewable energy "
            "not just environmentally preferable but economically attractive.\n\n"
            "However, the widespread adoption of renewable energy faces several significant challenges. Chief "
            "among these is the issue of intermittency: unlike coal or natural gas plants, solar and wind power "
            "generation is dependent on weather conditions. On cloudy days or when wind speeds are low, these "
            "sources may fail to meet electricity demand. This variability requires the development of sophisticated "
            "energy storage systems and smarter electrical grids.\n\n"
            "Battery storage technology has emerged as a crucial solution to the intermittency problem. "
            "Lithium-ion batteries, originally developed for consumer electronics, have been scaled up to create "
            "massive grid-scale storage facilities. Tesla's Hornsdale Power Reserve in South Australia, for example, "
            "was one of the first large-scale battery installations and has demonstrably improved grid stability in "
            "the region. More recently, flow batteries and other alternative storage technologies have shown promise "
            "for long-duration energy storage.\n\n"
            "Another challenge relates to infrastructure. The existing electricity grid in many countries was "
            "designed for centralised power generation—large power stations feeding electricity to consumers through "
            "a one-way network. Integrating large amounts of renewable energy requires a fundamental redesign of "
            "this infrastructure to accommodate distributed generation, where power can flow in multiple directions. "
            "This transition requires substantial investment and coordinated planning between governments, utilities, "
            "and technology companies.\n\n"
            "Despite these challenges, the momentum behind renewable energy appears unstoppable. Many countries "
            "have set ambitious targets for carbon neutrality, and renewable energy is central to achieving these "
            "goals. Investment in clean energy technologies reached a record $1.7 trillion in 2023, surpassing "
            "fossil fuel investment for the first time. The question is no longer whether renewable energy will "
            "dominate the future energy landscape, but how quickly this transition can be managed and what policies "
            "will best support it."
        ),
        'questions': [
            {
                'type': 'true_false_ng',
                'label': 'Part A: True / False / Not Given',
                'instruction': (
                    "次の各文について、パッセージの内容と照らし合わせ、\n"
                    "  TRUE       = パッセージの内容と一致する\n"
                    "  FALSE      = パッセージの内容と矛盾する\n"
                    "  NOT GIVEN  = パッセージに情報がない\n"
                    "と入力してください（T / F / NG でも可）。"
                ),
                'items': [
                    {
                        'q': '1. Solar PV panel costs have decreased by more than 90% since 2010.',
                        'answer': 'TRUE',
                        'alt': ['TRUE', 'T'],
                        'explanation': '第2段落 "The cost of solar photovoltaic (PV) panels has fallen by more than 90% since 2010" と一致。'
                    },
                    {
                        'q': '2. Renewable energy now accounts for more than half of global electricity generation.',
                        'answer': 'FALSE',
                        'alt': ['FALSE', 'F'],
                        'explanation': '第1段落では "approximately 30%" と記載。50%以上は誤り。'
                    },
                    {
                        'q': '3. The Hornsdale Power Reserve uses flow battery technology.',
                        'answer': 'FALSE',
                        'alt': ['FALSE', 'F'],
                        'explanation': '第4段落：Hornsdale はリチウムイオン電池。フロー電池は "recently" 登場した別の技術。'
                    },
                    {
                        'q': '4. Investment in clean energy exceeded fossil fuel investment for the first time in 2023.',
                        'answer': 'TRUE',
                        'alt': ['TRUE', 'T'],
                        'explanation': '最終段落 "surpassing fossil fuel investment for the first time" と一致。'
                    },
                    {
                        'q': '5. Several governments have already achieved carbon neutrality.',
                        'answer': 'NOT GIVEN',
                        'alt': ['NOT GIVEN', 'NG'],
                        'explanation': 'パッセージは carbon neutrality の「目標」には触れるが、達成した国については記述なし。'
                    },
                ]
            },
            {
                'type': 'multiple_choice',
                'label': 'Part B: Multiple Choice',
                'instruction': '最も適切な答えを A〜D の中から選んでください。',
                'items': [
                    {
                        'q': '6. According to the passage, what is described as the MAIN challenge for renewable energy?',
                        'options': [
                            'A. High manufacturing costs',
                            'B. Lack of government support',
                            'C. Dependence on weather conditions',
                            'D. Shortage of raw materials',
                        ],
                        'answer': 'C',
                        'explanation': '第3段落 "Chief among these is the issue of intermittency" → 天候への依存性が主な課題。'
                    },
                    {
                        'q': '7. What does the passage say about the existing electricity grid?',
                        'options': [
                            'A. It was built specifically for renewable energy',
                            'B. It was designed for centralised power generation',
                            'C. It already supports distributed generation',
                            'D. It is funded by private companies only',
                        ],
                        'answer': 'B',
                        'explanation': '第5段落 "designed for centralised power generation" と明記。'
                    },
                    {
                        'q': '8. The word "intermittency" (paragraph 3) is closest in meaning to:',
                        'options': [
                            'A. unreliability due to inconsistent output',
                            'B. high cost of production',
                            'C. negative environmental impact',
                            'D. technical complexity of systems',
                        ],
                        'answer': 'A',
                        'explanation': '間欠性 = 天候によって発電量が不安定なこと → A が最も近い意味。'
                    },
                ]
            },
            {
                'type': 'short_answer',
                'label': 'Part C: Short Answer (3語以内)',
                'instruction': '以下の質問にパッセージから3語以内で答えてください。',
                'items': [
                    {
                        'q': '9. What percentage of global electricity came from renewables in 2023?',
                        'answer': '30%',
                        'keywords': ['30'],
                        'explanation': '第1段落 "approximately 30% of global electricity generation"'
                    },
                    {
                        'q': '10. What was the original purpose of lithium-ion batteries before grid storage?',
                        'answer': 'consumer electronics',
                        'keywords': ['consumer', 'electronics'],
                        'explanation': '第4段落 "originally developed for consumer electronics"'
                    },
                ]
            }
        ],
        'band7_tips': [
            'TRUE/FALSE/NG: テキストに書かれていないことは絶対 NOT GIVEN。自分の知識で判断しない！',
            'キーワードをスキャンして答えが含まれる段落を素早く特定し、精読する。',
            '選択肢の言い換え (paraphrase) に注意。正解は同じ意味でも別の単語で書かれていることが多い。',
            '時間配分: 20分で1パッセージ。1問1〜1.5分が目安。時間がかかる問題はスキップして後で戻る。',
        ]
    },
    {
        'id': 2,
        'title': 'Passage 2: The Psychology of Procrastination',
        'level': 'Academic',
        'time_limit': 20,
        'text': (
            "Procrastination—the act of unnecessarily delaying tasks despite knowing the negative consequences"
            "—is a phenomenon that affects an estimated 20% of adults chronically and up to 95% of people "
            "occasionally. Despite its prevalence, procrastination is frequently misunderstood as a time "
            "management problem or a character flaw indicating laziness. Recent psychological research, "
            "however, suggests a far more complex picture.\n\n"
            "Dr. Fuschia Sirois, a professor at Durham University, argues that procrastination is fundamentally "
            "an emotion regulation problem rather than a productivity issue. When faced with a task that triggers "
            "negative emotions—anxiety, boredom, self-doubt, or frustration—the procrastinating individual "
            "prioritises short-term mood relief over long-term goals. The avoidance behaviour provides immediate "
            "emotional relief, even though it creates greater stress and negative consequences in the future.\n\n"
            "Neuroscientific research has shed light on the brain mechanisms involved. The limbic system, which "
            "governs our emotional responses, often overpowers the prefrontal cortex, responsible for rational "
            "decision-making and long-term planning. Individuals who procrastinate more frequently tend to show "
            "stronger amygdala activity—the brain region associated with fear and emotional processing—in "
            "response to challenging tasks. This neural imbalance means that for many procrastinators, the "
            "emotional aversion to a task can feel genuinely overwhelming.\n\n"
            "The relationship between procrastination and self-compassion is particularly noteworthy. Research "
            "by Dr. Kristin Neff and colleagues has demonstrated that individuals who treat themselves with "
            "kindness after procrastinating are actually less likely to procrastinate in the future. Harsh "
            "self-criticism, paradoxically, tends to worsen procrastination by increasing negative emotions—"
            "the very thing that triggered the avoidance behaviour in the first place. This finding has "
            "significant implications for how we approach productivity and self-improvement.\n\n"
            "Perfectionism is another psychological factor closely linked to procrastination. Contrary to "
            "popular belief, perfectionists are not necessarily more productive; rather, the fear of producing "
            "imperfect work can lead to paralysis. Studies have found that there are two types of perfectionist "
            "procrastinators: those who delay starting because they fear failure, and those who delay finishing "
            "because they fear judgement of the completed work. Both patterns represent adaptive strategies "
            "gone wrong.\n\n"
            "Understanding procrastination as an emotional phenomenon rather than a moral failing opens up "
            "new avenues for treatment. Therapeutic approaches such as Acceptance and Commitment Therapy (ACT) "
            "and Cognitive Behavioural Therapy (CBT) have shown effectiveness in reducing procrastination by "
            "helping individuals develop a different relationship with uncomfortable emotions. Rather than trying "
            "to eliminate the negative feelings associated with difficult tasks, these therapies encourage "
            "acceptance of such feelings while still taking purposeful action."
        ),
        'questions': [
            {
                'type': 'true_false_ng',
                'label': 'Part A: True / False / Not Given',
                'instruction': (
                    "TRUE / FALSE / NOT GIVEN （または T / F / NG）で答えてください。"
                ),
                'items': [
                    {
                        'q': '1. Approximately one in five adults suffer from chronic procrastination.',
                        'answer': 'TRUE',
                        'alt': ['TRUE', 'T'],
                        'explanation': '"affects an estimated 20% of adults chronically" → 20% = 1 in 5。'
                    },
                    {
                        'q': '2. Dr. Sirois believes procrastination is primarily caused by poor time management.',
                        'answer': 'FALSE',
                        'alt': ['FALSE', 'F'],
                        'explanation': 'Sirois博士は "emotion regulation problem" と述べており、時間管理の問題とは否定。'
                    },
                    {
                        'q': '3. Procrastinators tend to have a smaller amygdala than non-procrastinators.',
                        'answer': 'NOT GIVEN',
                        'alt': ['NOT GIVEN', 'NG'],
                        'explanation': 'パッセージは扁桃体の「活動が強い」とは述べるが、サイズには言及なし。'
                    },
                    {
                        'q': '4. Self-compassion after procrastinating can reduce the likelihood of future procrastination.',
                        'answer': 'TRUE',
                        'alt': ['TRUE', 'T'],
                        'explanation': '"individuals who treat themselves with kindness … are actually less likely to procrastinate in the future"'
                    },
                    {
                        'q': '5. CBT is the most effective therapy for treating procrastination.',
                        'answer': 'NOT GIVEN',
                        'alt': ['NOT GIVEN', 'NG'],
                        'explanation': 'ACT と CBT 両方が有効とされるが、どちらが「最も効果的」かは述べられていない。'
                    },
                ]
            },
            {
                'type': 'multiple_choice',
                'label': 'Part B: Multiple Choice',
                'instruction': '最も適切な答えを A〜D から選んでください。',
                'items': [
                    {
                        'q': '6. Why does avoidance behaviour occur, according to the passage?',
                        'options': [
                            'A. To achieve long-term productivity goals',
                            'B. To gain immediate emotional relief',
                            'C. To avoid social interaction',
                            'D. To improve concentration',
                        ],
                        'answer': 'B',
                        'explanation': '第2段落 "The avoidance behaviour provides immediate emotional relief"'
                    },
                    {
                        'q': '7. What does the passage say about perfectionist procrastinators?',
                        'options': [
                            'A. They are always the most productive workers',
                            'B. They never complete any work at all',
                            'C. They can delay either starting or finishing tasks',
                            'D. They are primarily motivated by fear of success',
                        ],
                        'answer': 'C',
                        'explanation': '第5段落：開始を遅らせる人と完成を遅らせる人の2タイプが存在する。'
                    },
                ]
            },
            {
                'type': 'matching',
                'label': 'Part C: Matching (脳の部位と機能)',
                'instruction': (
                    "以下の脳の部位（A〜C）と機能の説明（1〜3）を正しく結びつけてください。\n"
                    "例：A=1, B=3, C=2"
                ),
                'items': [
                    {
                        'concepts': ['A. Limbic system', 'B. Prefrontal cortex', 'C. Amygdala'],
                        'descriptions': [
                            '1. Responsible for rational decision-making and long-term planning',
                            '2. Associated with fear and emotional processing',
                            '3. Governs overall emotional responses',
                        ],
                        'answers': {'A': '3', 'B': '1', 'C': '2'},
                        'explanation': (
                            '第3段落より:\n'
                            '  A. Limbic system = "governs our emotional responses" → 3\n'
                            '  B. Prefrontal cortex = "rational decision-making and long-term planning" → 1\n'
                            '  C. Amygdala = "associated with fear and emotional processing" → 2'
                        )
                    }
                ]
            }
        ],
        'band7_tips': [
            'マッチング問題：選択肢を全部先に読んでからパッセージを読む。',
            '否定語（not, never, rarely, contrary to）を見落とすと全く逆の答えになる。要注意！',
            '段落の最初と最後の文にトピックの核心が来ることが多い（トピックセンテンス）。',
            '同義語・反義語の知識が合否を左右する。Academic Word List を毎日少しずつ覚えよう。',
        ]
    }
]


# ─────────────────────────────────────────────
# ─── リスニングデータ ─────────────────────────
# ─────────────────────────────────────────────
LISTENING_SECTIONS = [
    {
        'id': 1,
        'title': 'Section 1: Booking a Gym Membership',
        'description': '日常的な会話（ジムへの入会手続き）です。\n情報を正確に把握し、空欄を埋めましょう。',
        'transcript': """\
RECEPTIONIST: Good morning! Welcome to FitLife Gym. How can I help you today?

CUSTOMER: Hi, I'd like to get information about joining the gym. A friend recommended it.

RECEPTIONIST: Of course! We have several membership options. Our most popular is the Standard
membership at £45 per month, which gives you access to all equipment and group classes.

CUSTOMER: That sounds good. What are the opening hours?

RECEPTIONIST: We're open Monday to Friday from 6 am to 10 pm, and weekends from 8 am to 8 pm.
We're closed on Bank Holidays.

CUSTOMER: OK. And is there a joining fee?

RECEPTIONIST: Yes, there's a one-time joining fee of £30. However, if you sign up this month,
we're waiving it completely.

CUSTOMER: Oh, that's great! What about parking?

RECEPTIONIST: We have a car park with 50 spaces, completely free for members. The entrance is
on Maple Street, not the main road.

CUSTOMER: Perfect. Can I visit before I commit?

RECEPTIONIST: Absolutely. Just bring a photo ID and we'll give you a free trial for one day.
You'll need to book it in advance though—call us or go to our website at fitlifegym.co.uk.

CUSTOMER: What's your phone number?

RECEPTIONIST: It's 0800 443 217. That's 0800 443 217. We're happy to help with any questions!

CUSTOMER: And if I want to cancel, how much notice do I need to give?

RECEPTIONIST: We require 30 days written notice to cancel. You can send it by email or post.

CUSTOMER: Great. I think I'd like to sign up today. What do I need?

RECEPTIONIST: Just a valid ID, a bank card for the direct debit, and a recent utility bill or
bank statement as proof of address. We'll have you ready to work out within 20 minutes!""",
        'questions': [
            {
                'type': 'fill_blank',
                'label': 'Part A: Fill in the Blanks',
                'instruction': 'トランスクリプトを読み、空欄に入る語句を記入してください（1〜3語）。',
                'items': [
                    {
                        'q': '1. Monthly cost of Standard membership: £_______',
                        'answer': '45',
                        'keywords': ['45'],
                        'explanation': '"Standard membership at £45 per month"'
                    },
                    {
                        'q': '2. Weekday closing time: _______ pm',
                        'answer': '10',
                        'keywords': ['10'],
                        'explanation': '"Monday to Friday from 6 am to 10 pm"'
                    },
                    {
                        'q': '3. This month, the joining fee is being _______.',
                        'answer': 'waived',
                        'keywords': ['waived', 'waiving', 'waive'],
                        'explanation': '"we\'re waiving it completely"'
                    },
                    {
                        'q': '4. Car park entrance location: _______ Street',
                        'answer': 'Maple',
                        'keywords': ['maple'],
                        'explanation': '"The entrance is on Maple Street"'
                    },
                    {
                        'q': '5. Notice period required to cancel membership: _______ days',
                        'answer': '30',
                        'keywords': ['30'],
                        'explanation': '"We require 30 days written notice to cancel"'
                    },
                    {
                        'q': '6. Proof of address required: a recent _______ or bank statement',
                        'answer': 'utility bill',
                        'keywords': ['utility', 'bill'],
                        'explanation': '"a recent utility bill or bank statement as proof of address"'
                    },
                ]
            },
            {
                'type': 'multiple_choice',
                'label': 'Part B: Multiple Choice',
                'instruction': '最も適切な答えを A〜C から選んでください。',
                'items': [
                    {
                        'q': '7. How can a customer book a free trial day?',
                        'options': [
                            'A. Walk in without an appointment',
                            'B. Call or visit the website',
                            'C. Send an email request',
                        ],
                        'answer': 'B',
                        'explanation': '"call us or go to our website"'
                    },
                    {
                        'q': '8. What is the gym\'s correct phone number?',
                        'options': [
                            'A. 0800 434 217',
                            'B. 0800 443 712',
                            'C. 0800 443 217',
                        ],
                        'answer': 'C',
                        'explanation': '"It\'s 0800 443 217. That\'s 0800 443 217." — 繰り返し確認されている。'
                    },
                ]
            }
        ],
        'band7_tips': [
            'Section 1は最も易しい。数字・固有名詞（電話番号、住所）を正確に書き取る練習をしよう。',
            '答えは会話の順番に出てくることが多い。問題を先読みして何を探すか準備しておく。',
            'スペルミスは不正解になる。特に固有名詞（Maple、utility）は注意。',
            '聞き間違いやすい数字のペア (40/14, 30/13 など) に特に集中しよう。',
        ]
    },
    {
        'id': 2,
        'title': 'Section 3: University Group Discussion – Urban Farming',
        'description': '大学の指導教員と学生の学術的な討論です。\n複数の話者の意見・データを正確に把握しましょう。',
        'transcript': """\
TUTOR: Right, so today I want you to discuss your research project on urban farming.
Emma, Marcus—what have you found so far?

EMMA: We've been looking at vertical farming systems in cities. The main advantage we identified
is that they can produce food year-round regardless of weather conditions, which is really
significant for food security.

MARCUS: I'd add that transport costs are dramatically reduced when food is grown close to where
it's consumed. One study we found showed that conventionally grown food travels an average of
1,500 miles before it reaches the consumer. With urban farms, that's reduced to virtually zero.

TUTOR: Interesting. What about the challenges?

EMMA: The biggest issue is energy consumption. Vertical farms need artificial lighting for up to
20 hours a day, which makes them extremely energy-intensive. Unless powered by renewables, they
could actually have a worse carbon footprint than conventional farming.

MARCUS: The startup costs are also enormous. The technology—LED lighting systems, climate control,
hydroponic or aeroponic growing systems—requires substantial initial investment that many
entrepreneurs simply can't afford.

TUTOR: So what's your overall conclusion about the viability of urban farming?

EMMA: We think it has real potential, but only in specific contexts. For high-value crops like
herbs, microgreens, and leafy vegetables, it's already commercially viable in many cities.

MARCUS: But for staple crops like wheat or rice, it just doesn't make economic sense yet.
The yield per square metre isn't high enough to justify the costs.

TUTOR: That's a nuanced view. Have you looked at any successful case studies?

EMMA: Yes—Bowery Farming in New York uses 95% less water than traditional agriculture and
produces crops 365 days a year. They've managed to attract significant investment and are
expanding rapidly.

MARCUS: And in Japan, there are over 200 registered plant factories now. Many were actually
established after the 2011 earthquake and tsunami destroyed traditional farmland in some
regions—so it was partly a necessity-driven innovation.

TUTOR: Excellent research. For your final report, make sure you address the policy implications
—what support from local government would be needed to scale urban farming.

EMMA: We were planning to include that. We've found some interesting examples from Singapore
and the Netherlands where government subsidies have really accelerated development.""",
        'questions': [
            {
                'type': 'multiple_choice',
                'label': 'Part A: Multiple Choice',
                'instruction': '最も適切な答えを A〜D から選んでください。',
                'items': [
                    {
                        'q': '1. What does Marcus identify as a key advantage of urban farming?',
                        'options': [
                            'A. It requires no technology investment',
                            'B. It significantly reduces transport costs',
                            'C. It is always powered by renewable energy',
                            'D. It produces all types of crops more efficiently',
                        ],
                        'answer': 'B',
                        'explanation': '"transport costs are dramatically reduced when food is grown close to where it\'s consumed"'
                    },
                    {
                        'q': '2. According to Emma, why might vertical farming have a worse carbon footprint?',
                        'options': [
                            'A. It uses too much water',
                            'B. It requires transporting heavy equipment',
                            'C. It needs high energy for artificial lighting',
                            'D. It produces chemical waste',
                        ],
                        'answer': 'C',
                        'explanation': '"need artificial lighting for up to 20 hours a day, which makes them extremely energy-intensive"'
                    },
                    {
                        'q': '3. Which crops do the students say are already commercially viable in urban farms?',
                        'options': [
                            'A. Wheat and rice',
                            'B. Potatoes and corn',
                            'C. Herbs, microgreens, and leafy vegetables',
                            'D. All types of vegetables equally',
                        ],
                        'answer': 'C',
                        'explanation': '"high-value crops like herbs, microgreens, and leafy vegetables, it\'s already commercially viable"'
                    },
                ]
            },
            {
                'type': 'fill_blank',
                'label': 'Part B: Fill in the Blanks',
                'instruction': 'トランスクリプトから正確な情報を抜き出してください。',
                'items': [
                    {
                        'q': '4. Bowery Farming uses ______% less water than traditional agriculture.',
                        'answer': '95',
                        'keywords': ['95'],
                        'explanation': '"Bowery Farming in New York uses 95% less water than traditional agriculture"'
                    },
                    {
                        'q': '5. There are over _______ registered plant factories in Japan.',
                        'answer': '200',
                        'keywords': ['200'],
                        'explanation': '"there are over 200 registered plant factories now"'
                    },
                    {
                        'q': '6. Japan\'s plant factories expanded partly because of the 2011 _______ and tsunami.',
                        'answer': 'earthquake',
                        'keywords': ['earthquake'],
                        'explanation': '"after the 2011 earthquake and tsunami destroyed traditional farmland"'
                    },
                    {
                        'q': '7. Conventionally grown food travels an average of _______ miles to reach consumers.',
                        'answer': '1500',
                        'keywords': ['1500', '1,500'],
                        'explanation': '"food travels an average of 1,500 miles before it reaches the consumer"'
                    },
                ]
            }
        ],
        'band7_tips': [
            'Section 3は学術的議論。各話者が「同意・反論・補足」のどれをしているか意識して読む。',
            '数字・統計データはほぼ必ず出題される。会話中の数字をすべてメモする習慣をつけよう。',
            '話者が誰かを混同しないよう、Emma/Marcus/Tutor の発言をしっかり区別する。',
            'IELTS Listening では答えが paraphrase（言い換え）されていることが多い。原文のキーワードにとらわれすぎない。',
        ]
    }
]


# ─────────────────────────────────────────────
# ─── 語彙データ ───────────────────────────────
# ─────────────────────────────────────────────
VOCAB_LIST = [
    {'word': 'analyse',       'def': '詳しく調べる、分析する',           'ex': 'Scientists analyse data to find patterns.',                  'syn': ['examine', 'investigate']},
    {'word': 'approach',      'def': '方法、取り組み方；近づく',          'ex': 'The new approach to teaching improved results.',             'syn': ['method', 'strategy']},
    {'word': 'assess',        'def': '評価する、査定する',                'ex': 'Teachers assess students through exams and projects.',       'syn': ['evaluate', 'measure']},
    {'word': 'assume',        'def': '〜と仮定する、推測する',            'ex': 'Do not assume the answer without evidence.',                 'syn': ['presume', 'suppose']},
    {'word': 'benefit',       'def': '利益、恩恵；役に立つ',              'ex': 'Exercise has many benefits for mental health.',              'syn': ['advantage', 'gain']},
    {'word': 'challenge',     'def': '課題、難問；挑戦する',              'ex': 'Climate change is a major global challenge.',                'syn': ['difficulty', 'obstacle']},
    {'word': 'complex',       'def': '複雑な',                           'ex': 'The issue is more complex than it appears.',                  'syn': ['complicated', 'intricate']},
    {'word': 'concept',       'def': '概念、考え方',                     'ex': 'The concept of democracy is widely debated.',                'syn': ['idea', 'notion']},
    {'word': 'consequence',   'def': '結果、影響',                       'ex': 'Pollution has serious consequences for wildlife.',            'syn': ['result', 'outcome']},
    {'word': 'considerable',  'def': 'かなりの、相当な',                 'ex': 'There has been considerable progress in medicine.',           'syn': ['significant', 'substantial']},
    {'word': 'context',       'def': '文脈、状況、背景',                 'ex': 'Understanding context is essential for reading.',             'syn': ['background', 'setting']},
    {'word': 'contribute',    'def': '貢献する、一役買う',                'ex': 'Everyone can contribute to reducing waste.',                  'syn': ['add to', 'support']},
    {'word': 'demonstrate',   'def': 'を示す、証明する',                  'ex': 'Research demonstrates a link between diet and health.',       'syn': ['show', 'prove']},
    {'word': 'distinct',      'def': '明らかに異なる、明確な',            'ex': 'The two species are quite distinct from each other.',         'syn': ['different', 'separate']},
    {'word': 'emphasis',      'def': '強調、重点',                       'ex': 'The report placed emphasis on education funding.',             'syn': ['stress', 'focus']},
    {'word': 'evidence',      'def': '証拠、根拠',                       'ex': 'There is strong evidence that smoking causes cancer.',         'syn': ['proof', 'data']},
    {'word': 'factor',        'def': '要因、要素',                       'ex': 'Diet is a key factor in preventing disease.',                 'syn': ['element', 'component']},
    {'word': 'impact',        'def': '影響、衝撃；影響を与える',          'ex': 'Technology has a major impact on society.',                   'syn': ['effect', 'influence']},
    {'word': 'indicate',      'def': '示す、指し示す',                   'ex': 'The data indicates a rise in temperatures.',                  'syn': ['show', 'suggest']},
    {'word': 'interpret',     'def': '解釈する',                         'ex': 'It is easy to misinterpret statistics.',                      'syn': ['explain', 'translate']},
    {'word': 'maintain',      'def': '維持する、主張する',                'ex': 'It is important to maintain a healthy lifestyle.',            'syn': ['keep', 'sustain']},
    {'word': 'obtain',        'def': '手に入れる、獲得する',              'ex': 'Students must obtain a minimum score to pass.',               'syn': ['acquire', 'gain']},
    {'word': 'oppose',        'def': '反対する',                         'ex': 'Many residents oppose the new development.',                  'syn': ['resist', 'object to']},
    {'word': 'perceive',      'def': '知覚する、〜と見なす',              'ex': 'Risk is often perceived differently by different people.',     'syn': ['view', 'regard']},
    {'word': 'policy',        'def': '政策、方針',                       'ex': 'The government announced a new energy policy.',               'syn': ['plan', 'strategy']},
    {'word': 'principle',     'def': '原則、主義',                       'ex': 'The experiment follows the principles of science.',           'syn': ['rule', 'law']},
    {'word': 'process',       'def': '過程、手順；処理する',              'ex': 'The manufacturing process has been improved.',                'syn': ['procedure', 'method']},
    {'word': 'significant',   'def': '重要な、意義深い',                 'ex': 'There has been a significant increase in prices.',             'syn': ['important', 'notable']},
    {'word': 'sufficient',    'def': '十分な',                           'ex': 'The evidence is not sufficient to draw conclusions.',          'syn': ['adequate', 'enough']},
    {'word': 'vary',          'def': '変化する、異なる',                  'ex': 'Results vary depending on conditions.',                        'syn': ['differ', 'change']},
]


# ─────────────────────────────────────────────
# ─── リーディングモジュール ───────────────────
# ─────────────────────────────────────────────
class ReadingModule:
    def __init__(self, tracker: ProgressTracker):
        self.tracker = tracker

    def run(self):
        while True:
            clear()
            header("リーディング練習", "📖")
            print(f"\n  {C.cyan('IELTS Reading – Band 7 攻略')}")
            print(f"  {C.dim('各パッセージ20分が目安。本番は60分で3パッセージ。')}\n")
            divider()

            for i, p in enumerate(READING_PASSAGES):
                print(f"  {C.bold(str(i+1))}. {p['title']}")
                level = p['level']
                tl = p['time_limit']
                print(f"     {C.dim(f'レベル: {level} | 制限時間: {tl}分')}")

            print(f"\n  {C.bold('0')}. メインメニューに戻る")
            divider()

            choice = input(f"\n  {C.yellow('選択してください (0-{max})：'.replace('{max}', str(len(READING_PASSAGES))))} ").strip()
            if choice == '0':
                break
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(READING_PASSAGES):
                    self._do_passage(READING_PASSAGES[idx])
            except ValueError:
                pass

    def _do_passage(self, passage):
        clear()
        header(passage['title'], "📖")
        tl2 = passage["time_limit"]
        print(f"\n  {C.dim('制限時間:')}{C.yellow(f' {tl2}分')}")
        print(f"  {C.dim('本番形式では問題を先読みしてからパッセージを読む練習をしましょう。')}")
        pause("Enterを押してパッセージを表示する...")

        # パッセージ表示
        clear()
        print(f"\n{C.BOLD}{C.BLUE}{'─'*55}")
        print(f"  {passage['title']}")
        print(f"{'─'*55}{C.RESET}\n")
        wrap_print(passage['text'], width=72)

        start_time = time.time()
        pause("\nパッセージを読んだらEnterで問題へ...")

        # 問題セクション
        total_score = 0
        total_max = 0
        wrong_items = []

        for q_set in passage['questions']:
            score, max_s, wrongs = self._do_question_set(q_set)
            total_score += score
            total_max += max_s
            wrong_items.extend(wrongs)

        elapsed = (time.time() - start_time) / 60

        # 結果表示
        clear()
        header("リーディング 結果", "📊")
        pct = round(total_score / total_max * 100, 1) if total_max else 0
        band = pct_to_band(pct)
        bc = band_color(band)

        print(f"\n  スコア   : {C.bold(f'{total_score}/{total_max}')} ({pct}%)")
        print(f"  推定バンド: {bc}{C.bold(str(band))}{C.RESET}")
        print(f"  所要時間 : {elapsed:.1f}分")

        if band >= 7.0:
            print(f"\n  {C.green('🎉 素晴らしい！Band 7 レベルです！')}")
        elif band >= 6.0:
            print(f"\n  {C.yellow('📈 あと一歩！継続して練習しましょう。')}")
        else:
            print(f"\n  {C.red('💪 まだ差があります。解説を確認して復習しましょう。')}")

        # 間違えた問題の解説
        if wrong_items:
            print(f"\n{C.bold(C.red('─ 間違えた問題の解説 ─'))}")
            for item in wrong_items:
                print(f"\n  {C.yellow(item['q'])}")
                print(f"  {C.green('正解:')} {item['answer']}")
                print(f"  {C.dim('解説:')} {item['explanation']}")

        # Band 7 Tips
        print(f"\n{C.bold(C.cyan('─ Band 7 攻略ポイント ─'))}")
        for tip in passage['band7_tips']:
            print(f"  ✅ {tip}")

        # 記録保存
        self.tracker.add_score('reading', total_score, total_max, passage['title'])
        self.tracker.add_time(elapsed)

        pause()

    def _do_question_set(self, q_set):
        score = 0
        wrong = []

        clear()
        print(f"\n{C.bold(C.blue(q_set['label']))}")
        divider()
        wrap_print(q_set['instruction'])
        print()

        qtype = q_set['type']

        if qtype == 'true_false_ng':
            for item in q_set['items']:
                print(f"\n  {C.yellow(item['q'])}")
                ans = input(f"  あなたの答え (TRUE/FALSE/NOT GIVEN または T/F/NG): ").strip().upper()
                correct = ans in item['alt'] or ans == item['answer']
                if correct:
                    print(f"  {C.green('✓ 正解！')}")
                    score += 1
                else:
                    ans_val = item["answer"]
                    print(f"  {C.red(f'✗ 不正解。正解: {ans_val}')}")
                    wrong.append(item)
            return score, len(q_set['items']), wrong

        elif qtype == 'multiple_choice':
            for item in q_set['items']:
                print(f"\n  {C.yellow(item['q'])}")
                for opt in item['options']:
                    print(f"    {opt}")
                ans = input("  あなたの答え (A/B/C/D): ").strip().upper()
                if ans == item['answer']:
                    print(f"  {C.green('✓ 正解！')}")
                    score += 1
                else:
                    ans_val = item["answer"]
                    print(f"  {C.red(f'✗ 不正解。正解: {ans_val}')}")
                    wrong.append(item)
            return score, len(q_set['items']), wrong

        elif qtype == 'short_answer':
            for item in q_set['items']:
                print(f"\n  {C.yellow(item['q'])}")
                ans = input("  あなたの答え: ").strip().lower()
                correct = any(kw.lower() in ans for kw in item['keywords'])
                if correct:
                    print(f"  {C.green('✓ 正解！')}")
                    score += 1
                else:
                    ans_val = item["answer"]
                    print(f"  {C.red(f'✗ 不正解。正解: {ans_val}')}")
                    wrong.append(item)
            return score, len(q_set['items']), wrong

        elif qtype == 'matching':
            for item in q_set['items']:
                print("\n  概念:")
                for c in item['concepts']:
                    print(f"    {c}")
                print("\n  説明:")
                for d in item['descriptions']:
                    print(f"    {d}")
                print()
                correct_count = 0
                for concept_letter, correct_num in item['answers'].items():
                    ans = input(f"  {concept_letter} の番号: ").strip()
                    if ans == correct_num:
                        print(f"    {C.green('✓')}")
                        score += 1
                        correct_count += 1
                    else:
                        print(f"    {C.red(f'✗ 正解: {correct_num}')}")
                if correct_count < len(item['answers']):
                    wrong.append({
                        'q': 'マッチング問題',
                        'answer': str(item['answers']),
                        'explanation': item['explanation']
                    })
            total_possible = sum(len(it['answers']) for it in q_set['items'])
            return score, total_possible, wrong

        return 0, 0, []


# ─────────────────────────────────────────────
# ─── リスニングモジュール ─────────────────────
# ─────────────────────────────────────────────
class ListeningModule:
    def __init__(self, tracker: ProgressTracker):
        self.tracker = tracker

    def run(self):
        while True:
            clear()
            header("リスニング練習", "🎧")
            print(f"\n  {C.cyan('IELTS Listening – Band 7 攻略')}")
            print(f"  {C.dim('IELTSのListeningはSection 1〜4まで。難易度が上がります。')}")
            print(f"  {C.dim('※ このアプリではトランスクリプトを読みながら問題を解く形式です。')}\n")
            divider()

            for i, s in enumerate(LISTENING_SECTIONS):
                print(f"  {C.bold(str(i+1))}. {s['title']}")
                print(f"     {C.dim(s['description'].splitlines()[0])}")

            print(f"\n  {C.bold('0')}. メインメニューに戻る")
            divider()

            choice = input(f"\n  {C.yellow('選択してください (0-{max})：'.replace('{max}', str(len(LISTENING_SECTIONS))))} ").strip()
            if choice == '0':
                break
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(LISTENING_SECTIONS):
                    self._do_section(LISTENING_SECTIONS[idx])
            except ValueError:
                pass

    def _do_section(self, section):
        clear()
        header(section['title'], "🎧")
        wrap_print(section['description'])
        pause("Enterを押してトランスクリプトを表示する...")

        # トランスクリプト表示
        clear()
        print(f"\n{C.BOLD}{C.BLUE}{'─'*55}")
        print(f"  Transcript")
        print(f"{'─'*55}{C.RESET}\n")
        for line in section['transcript'].split('\n'):
            if ':' in line and line.split(':')[0].isupper():
                speaker, rest = line.split(':', 1)
                print(f"  {C.bold(C.cyan(speaker))}: {rest.strip()}")
            else:
                print(f"  {line}")
        print()

        start_time = time.time()
        pause("トランスクリプトを読んだらEnterで問題へ...")

        total_score = 0
        total_max = 0
        wrong_items = []

        for q_set in section['questions']:
            score, max_s, wrongs = self._do_question_set(q_set)
            total_score += score
            total_max += max_s
            wrong_items.extend(wrongs)

        elapsed = (time.time() - start_time) / 60

        # 結果表示
        clear()
        header("リスニング 結果", "📊")
        pct = round(total_score / total_max * 100, 1) if total_max else 0
        band = pct_to_band(pct)
        bc = band_color(band)

        print(f"\n  スコア   : {C.bold(f'{total_score}/{total_max}')} ({pct}%)")
        print(f"  推定バンド: {bc}{C.bold(str(band))}{C.RESET}")
        print(f"  所要時間 : {elapsed:.1f}分")

        if band >= 7.0:
            print(f"\n  {C.green('🎉 素晴らしい！Band 7 レベルです！')}")
        elif band >= 6.0:
            print(f"\n  {C.yellow('📈 あと一歩！数字と固有名詞の聞き取りを強化しよう。')}")
        else:
            print(f"\n  {C.red('💪 引き続き練習！解説を確認して弱点を克服しましょう。')}")

        if wrong_items:
            print(f"\n{C.bold(C.red('─ 間違えた問題の解説 ─'))}")
            for item in wrong_items:
                print(f"\n  {C.yellow(item['q'])}")
                print(f"  {C.green('正解:')} {item['answer']}")
                print(f"  {C.dim('解説:')} {item['explanation']}")

        print(f"\n{C.bold(C.cyan('─ Band 7 攻略ポイント ─'))}")
        for tip in section['band7_tips']:
            print(f"  ✅ {tip}")

        self.tracker.add_score('listening', total_score, total_max, section['title'])
        self.tracker.add_time(elapsed)

        pause()

    def _do_question_set(self, q_set):
        score = 0
        wrong = []

        clear()
        print(f"\n{C.bold(C.blue(q_set['label']))}")
        divider()
        wrap_print(q_set['instruction'])
        print()

        qtype = q_set['type']

        if qtype == 'fill_blank':
            for item in q_set['items']:
                print(f"\n  {C.yellow(item['q'])}")
                ans = input("  あなたの答え: ").strip().lower()
                correct = any(kw.lower() in ans for kw in item['keywords'])
                if correct:
                    print(f"  {C.green('✓ 正解！')}")
                    score += 1
                else:
                    ans_val = item["answer"]
                    print(f"  {C.red(f'✗ 不正解。正解: {ans_val}')}")
                    wrong.append(item)
            return score, len(q_set['items']), wrong

        elif qtype == 'multiple_choice':
            for item in q_set['items']:
                print(f"\n  {C.yellow(item['q'])}")
                for opt in item['options']:
                    print(f"    {opt}")
                ans = input("  あなたの答え (A/B/C): ").strip().upper()
                if ans == item['answer']:
                    print(f"  {C.green('✓ 正解！')}")
                    score += 1
                else:
                    ans_val = item["answer"]
                    print(f"  {C.red(f'✗ 不正解。正解: {ans_val}')}")
                    wrong.append(item)
            return score, len(q_set['items']), wrong

        return 0, 0, []


# ─────────────────────────────────────────────
# ─── 語彙モジュール ───────────────────────────
# ─────────────────────────────────────────────
class VocabularyModule:
    def __init__(self, tracker: ProgressTracker):
        self.tracker = tracker

    def run(self):
        while True:
            clear()
            header("語彙トレーニング", "📝")
            print(f"\n  {C.cyan('IELTS Academic Word List – 必須語彙 {n}語'.replace('{n}', str(len(VOCAB_LIST))))}")
            print(f"  {C.dim('Band 7 には幅広い語彙力と paraphrase 能力が必要です。')}\n")
            divider()
            print(f"  {C.bold('1')}. フラッシュカード（意味当て）")
            print(f"  {C.bold('2')}. 語彙クイズ（4択）")
            print(f"  {C.bold('3')}. 単語リスト一覧表示")
            print(f"  {C.bold('0')}. メインメニューに戻る")
            divider()

            choice = input(f"\n  {C.yellow('選択 (0-3): ')}").strip()
            if choice == '0':
                break
            elif choice == '1':
                self._flashcard_mode()
            elif choice == '2':
                self._quiz_mode()
            elif choice == '3':
                self._show_list()

    def _flashcard_mode(self):
        clear()
        header("フラッシュカード", "🃏")
        words = random.sample(VOCAB_LIST, min(10, len(VOCAB_LIST)))
        score = 0
        print(f"  {C.dim('単語の日本語の意味を入力してください。キーワードが含まれていれば正解。')}\n")

        for i, w in enumerate(words, 1):
            print(f"\n  {C.bold(C.cyan(f'[{i}/{len(words)}]'))} 単語: {C.bold(C.white(w['word']))}")
            print(f"  例文: {C.dim(w['ex'])}")
            ans = input("  意味を日本語で入力: ").strip()
            # 簡易採点：定義に含まれる主なキーワードを確認
            keywords = w['def'].replace('；', '、').replace('（', '').replace('）', '').split('、')
            correct = any(k.strip() in ans for k in keywords if len(k.strip()) > 1) or w['word'].lower() in ans.lower()
            # 少し柔軟に: 入力が空でなく、定義の一部でもOK
            def_kws = [k for k in w['def'].split() if len(k) > 1]

            if ans and (any(k in ans for k in w['def'].split('、')) or any(k in ans for k in def_kws)):
                correct = True

            if correct:
                print(f"  {C.green('✓ 正解！')} 意味: {w['def']}")
                print(f"  同義語: {', '.join(w['syn'])}")
                score += 1
            else:
                print(f"  {C.red('✗ 不正解。')} 正解: {C.yellow(w['def'])}")
                print(f"  同義語: {', '.join(w['syn'])}")

        pct = round(score / len(words) * 100, 1)
        print(f"\n{C.bold('─ 結果 ─')}")
        print(f"  {score}/{len(words)} 正解 ({pct}%)")
        self.tracker.add_score('vocab', score, len(words), 'フラッシュカード')
        self.tracker.add_time(5)
        pause()

    def _quiz_mode(self):
        clear()
        header("語彙4択クイズ", "❓")
        words = random.sample(VOCAB_LIST, min(10, len(VOCAB_LIST)))
        score = 0

        for i, w in enumerate(words, 1):
            clear()
            print(f"\n  {C.bold(C.cyan(f'[{i}/10]'))}")
            print(f"\n  次の単語の意味は？\n")
            print(f"  {C.bold(C.white('  ' + w['word'].upper()))}")
            print(f"\n  例文: {C.dim('  ' + w['ex'])}\n")

            # 4択を作成（正解1 + ランダム3）
            distractors = random.sample([v for v in VOCAB_LIST if v['word'] != w['word']], 3)
            options = [w] + distractors
            random.shuffle(options)
            correct_idx = None

            for j, opt in enumerate(options):
                label = chr(65 + j)  # A, B, C, D
                print(f"    {C.bold(label)}. {opt['def']}")
                if opt['word'] == w['word']:
                    correct_idx = label

            ans = input(f"\n  あなたの答え (A/B/C/D): ").strip().upper()
            if ans == correct_idx:
                print(f"  {C.green('✓ 正解！')}")
                score += 1
            else:
                print(f"  {C.red(f'✗ 不正解。正解: {correct_idx}')} → {w['def']}")
                print(f"  同義語: {', '.join(w['syn'])}")
            time.sleep(0.8)

        pct = round(score / 10 * 100, 1)
        clear()
        header("語彙クイズ 結果", "📊")
        band = pct_to_band(pct)
        bc = band_color(band)
        print(f"\n  スコア   : {C.bold(f'{score}/10')} ({pct}%)")
        print(f"  推定語彙レベル: {bc}{C.bold(str(band))}{C.RESET}")
        self.tracker.add_score('vocab', score, 10, '語彙4択クイズ')
        self.tracker.add_time(8)
        pause()

    def _show_list(self):
        clear()
        header("IELTS 必須語彙リスト", "📋")
        print(f"\n  {C.dim('Academic Word List より頻出語彙 {n}語'.replace('{n}', str(len(VOCAB_LIST))))}\n")
        divider()
        for w in VOCAB_LIST:
            print(f"  {C.bold(C.cyan(w['word'])):30s} {w['def']}")
            print(f"  {C.dim('  同義語: ' + ', '.join(w['syn']))}")
        divider()
        pause()


# ─────────────────────────────────────────────
# ─── Band 7 学習ガイド ────────────────────────
# ─────────────────────────────────────────────
def show_study_guide():
    clear()
    header("Band 7 攻略ガイド", "🎯")

    sections = [
        ("📖 READING の攻略", [
            "スキャニング: キーワードを文中で素早く探す技術を磨く",
            "スキミング: 段落全体の意味を速く把握する (15秒/段落)",
            "TRUE/FALSE/NG: 「書かれていないこと」= NOT GIVEN。自分の知識を使わない",
            "Matching Headings: パラグラフのメインアイデアを掴む練習",
            "時間配分: 20分/パッセージ。難問はスキップして戻る",
            "語彙力: Paraphrase (言い換え) を見抜く能力が必要",
        ]),
        ("🎧 LISTENING の攻略", [
            "先読み (prediction): 問題を先に読み、何を聞くか予測する",
            "数字・固有名詞: 電話番号・日付・金額は特に正確に",
            "話者の意見: 同意/反論/補足 を区別する",
            "スペル: 固有名詞のスペルミスは不正解になる",
            "Section 3&4: 学術語彙に慣れておく",
        ]),
        ("✍️  WRITING の攻略 (参考)", [
            "Task 1: データを客観的に記述。目立つ特徴を必ず含める",
            "Task 2: Intro→Body×2→Conclusionの4段落構成",
            "語彙の多様性: 同じ単語を繰り返さず、同義語を使う",
            "文法の正確性: 複文・関係代名詞・受動態を適切に使う",
        ]),
        ("🗣️  SPEAKING の攻略 (参考)", [
            "流暢さ: 沈黙を避け、つなぎ言葉 (well, actually) を活用",
            "語彙: 質問と同じ単語を避け、paraphrase する",
            "Part 2: 2分間話せるよう、アイデアを素早くまとめる練習",
            "発音: 正確さより流暢さと自然なリズムを意識する",
        ]),
        ("📅 学習スケジュール (週5日想定)", [
            "月: リーディング練習 (1パッセージ + 語彙30分)",
            "火: リスニング練習 (2セクション + 語彙30分)",
            "水: ライティング練習 (Task 2 エッセイ1本)",
            "木: リーディング練習 (1パッセージ) + スピーキング練習",
            "金: 弱点克服 + 語彙復習 + 模擬試験形式",
        ]),
    ]

    for title, points in sections:
        print(f"\n  {C.bold(C.blue(title))}")
        divider()
        for p in points:
            print(f"  • {p}")

    print(f"\n{C.bold(C.green('Band 7 スコア目標:'))}")
    print(f"  リーディング: 30問中 23問以上正解 (76%+)")
    print(f"  リスニング  : 40問中 30問以上正解 (75%+)")
    print(f"  ライティング: Task 2 で論理的・語彙豊かなエッセイ")
    print(f"  スピーキング: 流暢・正確・語彙豊かな2分間スピーチ")

    pause()


# ─────────────────────────────────────────────
# ─── メインアプリ ─────────────────────────────
# ─────────────────────────────────────────────
class IELTSApp:
    def __init__(self):
        self.tracker = ProgressTracker()
        self.reading  = ReadingModule(self.tracker)
        self.listening = ListeningModule(self.tracker)
        self.vocab    = VocabularyModule(self.tracker)

    def show_welcome(self):
        clear()
        print(f"""
{C.BOLD}{C.CYAN}
  ╔══════════════════════════════════════════════╗
  ║    IELTS Band 7 Master                       ║
  ║    4技能完全攻略アプリ                        ║
  ╚══════════════════════════════════════════════╝
{C.RESET}
  {C.yellow('目標: Band 7 (すべての技能で7.0以上)')}
  {C.dim('現在の重点: Reading & Listening')}

  {C.dim('このアプリでできること:')}
  • IELTS形式のリーディング演習 (True/False/NG, MC, Short Answer)
  • リスニング演習 (Fill-in-the-blank, 多肢選択)
  • Academic Word List 語彙トレーニング
  • 進捗トラッキングとバンドスコア推定
  • Band 7 攻略ガイド
""")
        pause("Enterを押してスタート...")

    def run(self):
        self.show_welcome()

        while True:
            clear()
            header("IELTS Band 7 Master", "🎓")

            # 直近のバンドを表示
            rb = self.tracker.estimate_band('reading')
            lb = self.tracker.estimate_band('listening')
            vb = self.tracker.estimate_band('vocab')

            def band_str(b):
                if b is None: return C.dim('未受験')
                return f"{band_color(b)}{b}{C.RESET}"

            print(f"\n  {C.dim('現在の推定バンド ─')}")
            print(f"  📖 Reading  : {band_str(rb)}   "
                  f"🎧 Listening : {band_str(lb)}   "
                  f"📝 語彙     : {band_str(vb)}")
            divider()
            print(f"\n  {C.bold('1')}. 📖  リーディング練習")
            print(f"  {C.bold('2')}. 🎧  リスニング練習")
            print(f"  {C.bold('3')}. 📝  語彙トレーニング")
            print(f"  {C.bold('4')}. 📊  学習ダッシュボード")
            print(f"  {C.bold('5')}. 🎯  Band 7 攻略ガイド")
            print(f"  {C.bold('0')}. アプリを終了する")
            divider()

            choice = input(f"\n  {C.yellow('選択してください (0-5): ')}").strip()

            if choice == '1':
                self.reading.run()
            elif choice == '2':
                self.listening.run()
            elif choice == '3':
                self.vocab.run()
            elif choice == '4':
                self.tracker.show_dashboard()
            elif choice == '5':
                show_study_guide()
            elif choice == '0':
                clear()
                print(f"\n{C.bold(C.cyan('  お疲れ様でした！継続は力なり。Band 7 目指して頑張りましょう！ 🎓'))}\n")
                sys.exit(0)


# ─────────────────────────────────────────────
if __name__ == '__main__':
    try:
        app = IELTSApp()
        app.run()
    except KeyboardInterrupt:
        print(f"\n\n{C.dim('  アプリを終了しました。')}\n")
        sys.exit(0)
