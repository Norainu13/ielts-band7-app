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
        ],
        'translation': (
            "【第1段落】再生可能エネルギー源は、過去20年間で目覚ましい変革を遂げてきた。"
            "かつては化石燃料の高価で信頼性の低い代替手段と見なされていた太陽光・風力発電は、"
            "今や世界の多くの地域でコスト競争力のある選択肢として台頭している。"
            "国際エネルギー機関（IEA）の報告によれば、2023年に再生可能エネルギーが世界の電力生産の"
            "約30%を占め、この数字は2030年までに大幅に上昇すると見込まれている。\n\n"
            "【第2段落】この転換を後押しする力は、技術的・経済的な両面にある。"
            "太陽光発電（PV）パネルのコストは、製造工程の改善と規模の経済化により、2010年以降90%以上下落した。"
            "同様に、風力タービン技術も大きく進歩し、現代の洋上タービンは最大15メガワットの電力を生成できる。"
            "これは数千世帯に供給できる量だ。こうした技術革新により、再生可能エネルギーは環境面だけでなく"
            "経済面でも魅力的な選択肢となった。\n\n"
            "【第3段落】しかし、再生可能エネルギーの普及にはいくつかの重大な課題がある。"
            "最大の課題は「間欠性」の問題だ。石炭や天然ガスの発電所と異なり、太陽光・風力発電は天候に依存する。"
            "曇りの日や風速が低い時には、電力需要を満たせないことがある。"
            "この変動性に対応するには、高度なエネルギー貯蔵システムとよりスマートな電力グリッドの開発が必要だ。\n\n"
            "【第4段落】バッテリー貯蔵技術は、間欠性問題の重要な解決策として台頭してきた。"
            "もともと民生用電子機器向けに開発されたリチウムイオン電池は、大規模なグリッド規模の貯蔵施設へと"
            "スケールアップされている。例えば南オーストラリア州のテスラ・ホーンズデール電力貯蔵施設は、"
            "大規模バッテリー設備の先駆けの一つであり、同地域のグリッド安定性を実証的に改善している。"
            "最近では、フロー電池などの代替貯蔵技術も長時間エネルギー貯蔵に有望な結果を示している。\n\n"
            "【第5段落】もう一つの課題はインフラに関するものだ。"
            "多くの国の既存電力網は、大型発電所から消費者へ一方向に電力を供給する「集中型発電」向けに設計されている。"
            "大量の再生可能エネルギーを統合するには、電力が複数方向に流れる「分散型発電」に対応した"
            "インフラの抜本的な再設計が必要だ。この移行には政府・電力会社・技術企業間の多大な投資と"
            "協調した計画が求められる。\n\n"
            "【第6段落】こうした課題にもかかわらず、再生可能エネルギーの勢いは止められないように見える。"
            "多くの国がカーボンニュートラルの野心的な目標を掲げており、再生可能エネルギーはその達成の中核を担う。"
            "クリーンエネルギー技術への投資は2023年に過去最高の1.7兆ドルに達し、初めて化石燃料投資を上回った。"
            "問題はもはや、再生可能エネルギーが将来のエネルギー地図を支配するかどうかではなく、"
            "この移行をいかに速やかに管理し、どの政策が最もうまくそれを後押しするかということだ。"
        )
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
        ],
        'translation': (
            "【第1段落】先延ばし——結果が分かっていながら不必要に課題を先延ばしにする行為——は、"
            "推定20%の成人が慢性的に、また最大95%の人が時折経験する現象だ。"
            "その蔓延度にもかかわらず、先延ばしはしばしば時間管理の問題や怠惰さを示す性格的欠陥として"
            "誤解される。しかし最近の心理学研究は、はるかに複雑な実態を示唆している。\n\n"
            "【第2段落】ダーラム大学教授のフュージャ・シロワ博士は、先延ばしは生産性の問題ではなく、"
            "本質的に感情調節の問題だと主張する。不安・退屈・自己不信・欲求不満など否定的感情を引き起こす"
            "課題に直面すると、先延ばしをする人は長期的な目標よりも短期的な気分の解消を優先する。"
            "回避行動は即座の感情的安堵をもたらすが、将来にはより大きなストレスと悪影響を生み出す。\n\n"
            "【第3段落】神経科学の研究は、関与する脳のメカニズムに光を当てている。"
            "感情反応を司る辺縁系は、合理的な意思決定と長期計画を担う前頭前野をしばしば上回る。"
            "先延ばしが多い人は、挑戦的な課題に対して恐怖や感情処理に関連する脳領域である扁桃体の活動が"
            "より強い傾向がある。この神経学的アンバランスにより、多くの先延ばし者にとって課題への"
            "感情的嫌悪は本当に圧倒的なものに感じられる。\n\n"
            "【第4段落】先延ばしと自己慈悲の関係は特に注目に値する。"
            "クリスティン・ネフ博士らの研究は、先延ばしをした後に自分に優しく接する人は実際には"
            "将来先延ばしをしにくいことを示している。逆説的に、厳しい自己批判は否定的感情を増大させることで"
            "先延ばしを悪化させる傾向がある——それがそもそも回避行動を引き起こしたものだ。"
            "この知見は、生産性と自己改善へのアプローチに重要な示唆をもたらす。\n\n"
            "【第5段落】完璧主義も先延ばしと密接に関連する心理的要因だ。"
            "一般的な通念に反し、完璧主義者が必ずしもより生産的というわけではない。"
            "むしろ不完全な仕事を生み出すことへの恐怖が麻痺状態を招くことがある。"
            "研究では、完璧主義的な先延ばし者には2つのタイプがあることが分かった。"
            "失敗を恐れて開始を遅らせるタイプと、完成した仕事が評価されることを恐れて"
            "完了を遅らせるタイプだ。どちらのパターンも、適応的な戦略が裏目に出たものだ。\n\n"
            "【第6段落】先延ばしを道徳的欠陥ではなく感情的現象として理解することで、"
            "新たな治療の道が開かれる。アクセプタンス＆コミットメント・セラピー（ACT）や"
            "認知行動療法（CBT）などの治療的アプローチは、辛い感情との向き合い方を変える支援をすることで"
            "先延ばしを減らす効果が示されている。困難な課題に伴う否定的感情を排除しようとするのではなく、"
            "こうした感情を受け入れながらも目的を持った行動を取ることをこれらの療法は促す。"
        )
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
    # AWL Sublist 1–4 追加語
    {'word': 'achieve',      'def': '達成する、成し遂げる',               'ex': 'Hard work is needed to achieve your goals.',                   'syn': ['accomplish', 'attain']},
    {'word': 'area',         'def': '分野、地域、領域',                   'ex': 'Research in this area has grown rapidly.',                     'syn': ['field', 'domain']},
    {'word': 'available',    'def': '利用可能な、入手できる',              'ex': 'Free information is widely available online.',                  'syn': ['accessible', 'obtainable']},
    {'word': 'consist',      'def': '〜から成る、構成される',              'ex': 'The team consists of experts from five countries.',             'syn': ['comprise', 'be made up of']},
    {'word': 'create',       'def': '創造する、作り出す',                  'ex': 'The project aims to create new job opportunities.',             'syn': ['produce', 'generate']},
    {'word': 'define',       'def': '定義する、明確にする',                'ex': 'It is important to define key terms at the start.',             'syn': ['explain', 'clarify']},
    {'word': 'derive',       'def': '引き出す、由来する',                  'ex': 'Many English words derive from Latin.',                         'syn': ['obtain', 'originate']},
    {'word': 'distribute',   'def': '分配する、配布する',                  'ex': 'Aid was distributed to the affected communities.',              'syn': ['allocate', 'spread']},
    {'word': 'environment',  'def': '環境、周囲の状況',                   'ex': 'Protecting the environment is a global priority.',               'syn': ['surroundings', 'setting']},
    {'word': 'establish',    'def': '設立する、確立する',                  'ex': 'The university was established in 1850.',                       'syn': ['found', 'set up']},
    {'word': 'estimate',     'def': '推定する、見積もる',                  'ex': 'Experts estimate the cost at five million dollars.',             'syn': ['calculate', 'approximate']},
    {'word': 'function',     'def': '機能、役割；機能する',                'ex': 'The function of the liver is to filter blood.',                  'syn': ['role', 'purpose']},
    {'word': 'identify',     'def': '特定する、識別する',                  'ex': 'Researchers identified three key risk factors.',                 'syn': ['recognise', 'pinpoint']},
    {'word': 'individual',   'def': '個人；個々の',                       'ex': 'Each individual has the right to free speech.',                  'syn': ['person', 'single']},
    {'word': 'involve',      'def': '含む、〜を必要とする',                'ex': 'The experiment involves a series of controlled tests.',          'syn': ['include', 'entail']},
    {'word': 'issue',        'def': '問題、課題；発行する',                'ex': 'Poverty is a serious social issue.',                            'syn': ['problem', 'matter']},
    {'word': 'labour',       'def': '労働、労働力',                       'ex': 'Child labour is prohibited in most countries.',                  'syn': ['work', 'workforce']},
    {'word': 'occur',        'def': '起こる、生じる',                     'ex': 'Major earthquakes occur along fault lines.',                     'syn': ['happen', 'take place']},
    {'word': 'percent',      'def': 'パーセント、割合',                   'ex': 'Forty percent of the population live in cities.',                'syn': ['proportion', 'ratio']},
    {'word': 'period',       'def': '期間、時代',                         'ex': 'The economy grew rapidly during this period.',                   'syn': ['time', 'era']},
    {'word': 'require',      'def': '必要とする、要求する',                'ex': 'The job requires strong communication skills.',                  'syn': ['need', 'demand']},
    {'word': 'research',     'def': '研究、調査',                         'ex': 'Further research is needed on this topic.',                      'syn': ['study', 'investigation']},
    {'word': 'respond',      'def': '応答する、反応する',                  'ex': 'The government responded quickly to the crisis.',                'syn': ['reply', 'react']},
    {'word': 'section',      'def': '部分、節、区域',                     'ex': 'The report is divided into four sections.',                      'syn': ['part', 'division']},
    {'word': 'sector',       'def': '分野、部門',                         'ex': 'The public sector employs millions of people.',                  'syn': ['industry', 'field']},
    {'word': 'structure',    'def': '構造、体制；組み立てる',              'ex': 'The structure of the essay should be clear.',                    'syn': ['framework', 'organisation']},
    {'word': 'theory',       'def': '理論、学説',                         'ex': 'Darwin\'s theory of evolution is widely accepted.',              'syn': ['hypothesis', 'concept']},
    # AWL Sublist 5–7
    {'word': 'abstract',     'def': '抽象的な；要旨',                     'ex': 'The argument was too abstract to understand.',                   'syn': ['theoretical', 'conceptual']},
    {'word': 'accurate',     'def': '正確な、精密な',                     'ex': 'The data must be accurate to be useful.',                        'syn': ['precise', 'exact']},
    {'word': 'adequate',     'def': '十分な、適切な',                     'ex': 'Adequate funding is essential for the project.',                 'syn': ['sufficient', 'satisfactory']},
    {'word': 'category',     'def': 'カテゴリー、分類',                   'ex': 'Items are sorted into different categories.',                    'syn': ['group', 'class']},
    {'word': 'conclude',     'def': '結論を出す、終わる',                  'ex': 'The study concludes that exercise reduces stress.',              'syn': ['determine', 'decide']},
    {'word': 'conduct',      'def': '行う、実施する；行動',                'ex': 'The team conducted a series of experiments.',                    'syn': ['carry out', 'perform']},
    {'word': 'data',         'def': 'データ、情報',                       'ex': 'The data shows a steady decline in birth rates.',                'syn': ['information', 'statistics']},
    {'word': 'debate',       'def': '議論、討論；議論する',                'ex': 'There is ongoing debate about climate policy.',                  'syn': ['discussion', 'argument']},
    {'word': 'decline',      'def': '減少する；衰退する；断る',            'ex': 'The population has declined by 10% over the decade.',            'syn': ['decrease', 'fall']},
    {'word': 'design',       'def': '設計する；デザイン',                  'ex': 'The building was designed by a famous architect.',               'syn': ['plan', 'create']},
    {'word': 'economy',      'def': '経済',                               'ex': 'The global economy is affected by trade policies.',              'syn': ['market', 'financial system']},
    {'word': 'efficient',    'def': '効率的な',                           'ex': 'Electric vehicles are more efficient than petrol cars.',          'syn': ['productive', 'effective']},
    {'word': 'expand',       'def': '拡大する、広げる',                   'ex': 'The company plans to expand into new markets.',                   'syn': ['grow', 'extend']},
    {'word': 'focus',        'def': '焦点を当てる；焦点',                  'ex': 'The report focuses on renewable energy.',                        'syn': ['concentrate', 'centre on']},
    {'word': 'generate',     'def': '生み出す、発生させる',                'ex': 'Solar panels generate electricity from sunlight.',               'syn': ['produce', 'create']},
    {'word': 'global',       'def': '世界規模の、地球全体の',              'ex': 'Global temperatures have risen over the past century.',          'syn': ['worldwide', 'international']},
    {'word': 'highlight',    'def': '強調する、際立たせる',                'ex': 'The report highlights the need for reform.',                     'syn': ['emphasise', 'underline']},
    {'word': 'impose',       'def': '課する、強制する',                   'ex': 'The government imposed new taxes on fuel.',                       'syn': ['enforce', 'implement']},
    {'word': 'income',       'def': '収入、所得',                         'ex': 'Low-income families struggle to afford housing.',                'syn': ['earnings', 'revenue']},
    {'word': 'legislation',  'def': '法律、立法',                         'ex': 'New legislation was passed to protect workers.',                 'syn': ['law', 'regulation']},
    {'word': 'method',       'def': '方法、手法',                         'ex': 'Scientists use a variety of methods to test ideas.',             'syn': ['approach', 'technique']},
    {'word': 'proportion',   'def': '割合、比率',                         'ex': 'A large proportion of students study online.',                   'syn': ['ratio', 'percentage']},
    {'word': 'publish',      'def': '出版する、発表する',                  'ex': 'The findings were published in a leading journal.',              'syn': ['release', 'issue']},
    {'word': 'range',        'def': '範囲、幅；及ぶ',                     'ex': 'The course covers a wide range of topics.',                      'syn': ['scope', 'variety']},
    {'word': 'reduce',       'def': '減らす、削減する',                   'ex': 'We must reduce carbon emissions immediately.',                    'syn': ['decrease', 'cut']},
    {'word': 'region',       'def': '地域、地方',                         'ex': 'The northern region has a colder climate.',                      'syn': ['area', 'zone']},
    {'word': 'regulate',     'def': '規制する、調整する',                  'ex': 'The industry is regulated by a government agency.',              'syn': ['control', 'manage']},
    {'word': 'relevant',     'def': '関連のある、適切な',                  'ex': 'Only include relevant information in your essay.',               'syn': ['related', 'pertinent']},
    {'word': 'resource',     'def': '資源、資料',                         'ex': 'Natural resources must be managed sustainably.',                  'syn': ['asset', 'supply']},
    {'word': 'role',         'def': '役割、機能',                         'ex': 'Education plays a vital role in development.',                   'syn': ['function', 'part']},
    {'word': 'source',       'def': '出所、情報源；由来する',              'ex': 'Always cite the source of your information.',                    'syn': ['origin', 'reference']},
    {'word': 'strategy',     'def': '戦略、方策',                         'ex': 'The government adopted a new economic strategy.',                'syn': ['plan', 'approach']},
    {'word': 'survey',       'def': '調査、アンケート；調査する',           'ex': 'A survey of 1,000 people was conducted.',                       'syn': ['study', 'poll']},
    {'word': 'sustainable',  'def': '持続可能な',                         'ex': 'Sustainable development meets present needs.',                   'syn': ['viable', 'renewable']},
    # AWL Sublist 8–10 & 高頻度IELTS語
    {'word': 'advocate',     'def': '主張する、支持する；支持者',           'ex': 'Many scientists advocate for stricter emissions rules.',          'syn': ['support', 'promote']},
    {'word': 'allocate',     'def': '割り当てる、配分する',                'ex': 'Funds were allocated to improve public transport.',              'syn': ['assign', 'distribute']},
    {'word': 'ambiguous',    'def': '曖昧な、多義的な',                   'ex': 'The law is ambiguous and needs clarification.',                   'syn': ['unclear', 'vague']},
    {'word': 'coherent',     'def': '一貫した、筋の通った',               'ex': 'A coherent argument is essential in academic writing.',           'syn': ['logical', 'consistent']},
    {'word': 'controversial', 'def': '議論を呼ぶ、論争的な',              'ex': 'Genetic engineering is a controversial topic.',                  'syn': ['disputed', 'debatable']},
    {'word': 'corporation',  'def': '大企業、法人',                       'ex': 'Large corporations have significant political influence.',        'syn': ['company', 'firm']},
    {'word': 'crucial',      'def': '極めて重要な',                       'ex': 'Early education is crucial for child development.',              'syn': ['vital', 'essential']},
    {'word': 'cultural',     'def': '文化的な',                           'ex': 'Cultural differences affect communication styles.',               'syn': ['social', 'traditional']},
    {'word': 'diverse',      'def': '多様な',                             'ex': 'The city has a diverse population from many countries.',          'syn': ['varied', 'mixed']},
    {'word': 'dominant',     'def': '支配的な、優勢な',                   'ex': 'English is the dominant language in international business.',     'syn': ['leading', 'prevailing']},
    {'word': 'enormous',     'def': '巨大な、莫大な',                     'ex': 'The project required an enormous amount of funding.',             'syn': ['huge', 'vast']},
    {'word': 'ethical',      'def': '倫理的な、道徳上の',                 'ex': 'Medical research must follow strict ethical guidelines.',         'syn': ['moral', 'principled']},
    {'word': 'evaluate',     'def': '評価する、判断する',                  'ex': 'It is important to evaluate sources critically.',                'syn': ['assess', 'judge']},
    {'word': 'evolve',       'def': '進化する、発展する',                  'ex': 'Language evolves as society changes.',                           'syn': ['develop', 'change']},
    {'word': 'exploit',      'def': '利用する、搾取する',                  'ex': 'Companies exploit natural resources for profit.',                'syn': ['use', 'take advantage of']},
    {'word': 'flexible',     'def': '柔軟な、融通の利く',                 'ex': 'Modern workplaces offer more flexible hours.',                    'syn': ['adaptable', 'versatile']},
    {'word': 'fundamental',  'def': '根本的な、基本的な',                 'ex': 'Access to clean water is a fundamental human right.',             'syn': ['basic', 'essential']},
    {'word': 'hypothesis',   'def': '仮説',                               'ex': 'The hypothesis was tested through experiments.',                  'syn': ['theory', 'assumption']},
    {'word': 'implement',    'def': '実施する、実行する',                  'ex': 'The new policy will be implemented next year.',                  'syn': ['carry out', 'execute']},
    {'word': 'incentive',    'def': '動機、奨励策',                       'ex': 'Tax incentives encourage businesses to hire more staff.',         'syn': ['motivation', 'reward']},
    {'word': 'inevitable',   'def': '避けられない、必然的な',              'ex': 'Change is inevitable in any growing organisation.',              'syn': ['unavoidable', 'certain']},
    {'word': 'infrastructure','def': 'インフラ、基盤施設',                 'ex': 'Poor infrastructure slows economic development.',                'syn': ['facilities', 'framework']},
    {'word': 'innovative',   'def': '革新的な、独創的な',                 'ex': 'Innovative solutions are needed to tackle climate change.',       'syn': ['creative', 'pioneering']},
    {'word': 'integrate',    'def': '統合する、組み込む',                  'ex': 'Technology should be integrated into classroom learning.',        'syn': ['combine', 'incorporate']},
    {'word': 'justify',      'def': '正当化する',                         'ex': 'You must justify your argument with evidence.',                  'syn': ['support', 'defend']},
    {'word': 'migrate',      'def': '移住する、移動する',                  'ex': 'Many people migrate to cities in search of work.',               'syn': ['move', 'relocate']},
    {'word': 'monitor',      'def': '監視する、観察する；モニター',         'ex': 'Doctors monitor patients\' progress closely.',                   'syn': ['observe', 'track']},
    {'word': 'moreover',     'def': 'さらに、加えて',                     'ex': 'The plan is costly; moreover, it may not work.',                  'syn': ['furthermore', 'in addition']},
    {'word': 'negative',     'def': '否定的な、マイナスの',               'ex': 'Pollution has a negative effect on public health.',               'syn': ['harmful', 'adverse']},
    {'word': 'objective',    'def': '目標；客観的な',                     'ex': 'The main objective is to reduce unemployment.',                  'syn': ['goal', 'aim']},
    {'word': 'potential',    'def': '可能性；潜在的な',                   'ex': 'Renewable energy has great potential for the future.',            'syn': ['possibility', 'capacity']},
    {'word': 'priority',     'def': '優先事項、優先度',                   'ex': 'Healthcare should be a top priority for the government.',         'syn': ['preference', 'concern']},
    {'word': 'promote',      'def': '促進する、宣伝する',                  'ex': 'Exercise promotes both physical and mental well-being.',          'syn': ['encourage', 'advance']},
    {'word': 'rely',         'def': '頼る、依存する',                     'ex': 'Many countries rely on fossil fuels for energy.',                 'syn': ['depend', 'count on']},
    {'word': 'restrict',     'def': '制限する、制約する',                  'ex': 'The new law restricts the use of single-use plastics.',           'syn': ['limit', 'constrain']},
    {'word': 'retain',       'def': '保持する、維持する',                  'ex': 'Companies must retain skilled workers to remain competitive.',    'syn': ['keep', 'maintain']},
    {'word': 'specify',      'def': '明示する、指定する',                  'ex': 'The contract specifies the terms of the agreement.',             'syn': ['state', 'detail']},
    {'word': 'stable',       'def': '安定した',                           'ex': 'A stable economy attracts foreign investment.',                  'syn': ['steady', 'secure']},
    {'word': 'statistic',    'def': '統計、データ',                       'ex': 'Statistics show that literacy rates have improved.',              'syn': ['figure', 'data']},
    {'word': 'subsequent',   'def': 'その後の、次の',                     'ex': 'Subsequent studies confirmed the original findings.',             'syn': ['following', 'later']},
    {'word': 'technology',   'def': '技術、テクノロジー',                  'ex': 'Technology has transformed the way we communicate.',             'syn': ['innovation', 'science']},
    {'word': 'transform',    'def': '変える、変革する',                   'ex': 'Digital technology has transformed the publishing industry.',     'syn': ['change', 'revolutionise']},
    {'word': 'trend',        'def': '傾向、トレンド',                     'ex': 'There is a growing trend towards remote working.',                'syn': ['tendency', 'pattern']},
    {'word': 'undermine',    'def': '損なう、弱体化させる',               'ex': 'Corruption undermines public trust in government.',               'syn': ['weaken', 'erode']},
    {'word': 'urban',        'def': '都市の、都会の',                     'ex': 'Urban areas face unique challenges such as overcrowding.',        'syn': ['city', 'metropolitan']},
    {'word': 'valid',        'def': '有効な、妥当な',                     'ex': 'A valid passport is required to travel abroad.',                 'syn': ['legitimate', 'sound']},
    {'word': 'welfare',      'def': '福祉、幸福',                         'ex': 'The government increased spending on child welfare.',             'syn': ['well-being', 'benefit']},
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
