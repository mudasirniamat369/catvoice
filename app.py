import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, g

app = Flask(__name__)
app.secret_key = 'thecatvoice_secret_key_2024_bisma'

DATABASE = 'tcv.db'

# ──────────────────────────────────────────────
#  Database helpers
# ──────────────────────────────────────────────

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    db = get_db()
    db.execute(query, args)
    db.commit()

# ──────────────────────────────────────────────
#  Settings helper
# ──────────────────────────────────────────────

def get_settings():
    rows = query_db('SELECT key, value FROM settings')
    return {row['key']: row['value'] for row in rows}

# ──────────────────────────────────────────────
#  Database initialisation
# ──────────────────────────────────────────────

STORIES = [
    (1,  'Pakistan & the Strait of Hormuz',               'Geopolitics',   'The waterway that controls the world\'s oil supply — and Pakistan\'s hidden role in the equation that mainstream media refuses to cover.',                                                                                                    'Pakistan sits at a critical geographic crossroads. The Strait of Hormuz — the narrow channel between Oman and Iran — carries roughly 20% of the world\'s oil supply. Every barrel that passes through this 33-kilometre-wide bottleneck shapes economies, governments, and wars.\n\nWhat mainstream media consistently ignores is Pakistan\'s invisible hand in this equation. Pakistan\'s deep-water Gwadar port, developed under CPEC, sits just 72 kilometres from the Strait. This proximity is not coincidental — it is strategic. China\'s Belt and Road Initiative was designed, in part, to create land-based alternatives to seaborne oil routes that could be blocked by the United States Navy.\n\nIf the Strait of Hormuz were ever closed, the global oil price would spike within hours. Pakistan, positioned as a corridor between China and the Arabian Sea, would become the most consequential geography in the world overnight.\n\nThe powers that control this narrative — the think tanks, the Western policy establishment, the financial media — have no incentive to explain Pakistan\'s leverage. A Pakistan that understands its own geopolitical value is a Pakistan that negotiates differently.\n\nThis is the truth they do not want you to see.',                                                                                                                                                                                                                                                                                                                                  '15.1K', '2024-10-15', 0),
    (2,  'Why I Love the Pakistani Passport',              'Reality Check', 'Challenging the narrative — a story of pride, identity, and the overlooked strength that lives inside a green booklet.',                                                                                                                      'Every travel influencer on the internet will show you the "world\'s most powerful passports" — the Japanese, the Singaporean, the German. The Pakistani passport is always near the bottom of these lists. And people share these lists with shame.\n\nI refuse that shame.\n\nA passport is not a measure of your worth. It is a colonial-era document that tells you which humans are allowed to move freely on a planet that none of us created. The hierarchies embedded in visa systems reflect power structures — not the character, intelligence, or potential of the people holding green booklets.\n\nThe Pakistani passport represents over 220 million people — engineers, doctors, artists, entrepreneurs, athletes, poets. People who built the Gulf states. People who power entire sectors of the British NHS. People who code in Silicon Valley.\n\nThe narrative that our passport is a source of shame is designed to make us look outward for validation rather than inward for strength. It is designed to make us measure ourselves by how easily we can leave — rather than how powerfully we can build.\n\nI love this passport. Not despite its ranking. But because of what it represents: a people that has survived, built, and refused to disappear, against every conceivable pressure.\n\nThat is not a weak passport story. That is one of the strongest stories on earth.',                                                                                                                                                                                                                                             '4.1M', '2024-09-01', 1),
    (3,  'Anjan Mat Bano — Wake Up',                       'Awareness',     'The uncomfortable truth about staying ignorant in a world that is actively on fire around you.',                                                                                                                                               'Ignorance has never been cheaper to maintain, and it has never been more expensive to afford.\n\nWe live in a world of infinite information and manufactured confusion. Algorithms are designed, specifically and deliberately, to keep you entertained rather than informed. The difference between those two things is everything.\n\nEntertained people do not ask questions. Entertained people do not organise. Entertained people do not resist.\n\n"Anjan mat bano" — do not be ignorant. This is not a judgement. It is an invitation. Because the systems that run the world count on you staying confused, distracted, and disengaged. Every time you click away from a news story and toward a funny reel, a decision has been made. Every time you say "yeh politics meri samajh se bahar hai" — another door closes.\n\nIgnorance protects no one. It only protects those who benefit from it.\n\nThe history of every oppressed people contains a moment — a critical, pivotal moment — when enough people finally decided to pay attention. That moment changed everything. We are at that moment right now. And the question is whether you choose to be conscious of it.',                                                                                                                                                                                    '100K', '2024-08-15', 0),
    (4,  'You Can Change Your Past',                       'Awareness',     'The science and philosophy of reframing your history — not erasing it, but transforming your relationship with it.',                                                                                                                           'Memory is not a recording. It is a reconstruction. Every time you remember something, you are not playing back a video file — you are rebuilding that experience from fragments, and the rebuilding process is influenced by who you are right now.\n\nThis is one of the most powerful findings in neuroscience, and almost nobody talks about it in the context of healing.\n\nYour past is not fixed. The events happened. But the meaning you assign to them, the story you tell yourself about them, the emotional weight they carry — all of that is malleable. Reconsolidation — the name science gives to this process — literally means that every time you access a memory, it becomes open to editing.\n\nThis does not mean you can pretend trauma did not happen. It means you have the power to change what it means to you.\n\nPeople who were abused as children can move from "I am broken" to "I survived something that should not have happened to me, and I am still here."\n\nPeople who failed publicly can move from "I am a failure" to "I learned what does not work."\n\nThe story you carry about your past shapes every decision you make about your future. You are the author. You always have been. Most people just have not been told they can pick up the pen.',                                                                                                                                         '19.5K', '2024-11-02', 0),
    (5,  'The Strait of Hormuz — Full Analysis',           'Geopolitics',   'A deep dive into the world\'s most dangerous chokepoint and why every global superpower is watching it right now.',                                                                                                                            'The Strait of Hormuz is 33 kilometres wide at its narrowest point. Through this channel flows approximately 20 million barrels of crude oil every single day. That number represents nearly 20% of all petroleum traded on earth.\n\nFive countries share its coastline and strategic influence: Iran, Oman, the United Arab Emirates, Bahrain, and Qatar. The United States maintains a massive naval presence in the region specifically to ensure this strait remains open. Iran has repeatedly threatened to close it. The world has repeatedly considered what that would mean.\n\nIf the Strait closes for even two weeks, the global price of oil doubles. Supply chains collapse. Economies that depend on Gulf oil — including most of Europe, India, China, Japan, and South Korea — would face immediate crisis.\n\nIran knows this. The United States knows Iran knows this. This is why the standoff has lasted for decades without full escalation: because the consequences of miscalculation are too catastrophic for anyone to risk.\n\nWhat America fears is not just a closed strait. It is the precedent. Because if Iran proves it can disrupt the global oil supply and survive, every other nation watching will draw a very specific conclusion about the limits of American power.\n\nThe Strait of Hormuz is not just geography. It is the most expensive lesson the world has not yet been forced to learn.',                                                                                                                                '28.8K', '2024-10-22', 0),
    (6,  'Rothschild\'s System — We Are Slaves',            'Conspiracy',    'Exposing the financial architecture that was designed to keep ordinary people dependent and powerless.',                                                                                                                                      'The Rothschild banking dynasty began in the 18th century in Frankfurt, Germany. By the 19th century, it had become the largest private banking network in the world, with branches in Frankfurt, London, Paris, Vienna, and Naples. At their peak, historians estimate they controlled wealth larger than the annual GDP of most nations.\n\nThis is not conspiracy. This is documented history.\n\nWhat becomes more contested — and more important — is the structural legacy. The Rothschilds and their contemporaries did not just accumulate money. They built the architecture of how money itself works. Central banking, fractional reserve lending, sovereign debt instruments — these were not natural evolutions. They were engineered systems.\n\nWhen a government borrows money from a central bank, it borrows with interest. That interest must be repaid — which means more money must be created — which creates more debt. This cycle was not an accident. It was a feature. A system of permanent, structural debt keeps nations dependent, keeps populations working, and keeps the architectural class in control.\n\nThe greatest trick the financial system ever pulled was convincing the world that it was simply "how economies work." It is not how economies have to work. It is how this particular design of economy was built to work.',                                                                                                                               '755',   '2024-12-01', 0),
    (7,  'How Rockefeller Designed the System You Live In', 'History',       'Medicine, food, education, and health — all shaped by one man\'s obsession with control and profit.',                                                                                                                                         'In 1910, the American Medical Association and the Carnegie Foundation funded a study called the Flexner Report. Its stated purpose was to evaluate medical schools across North America. Its actual effect was to eliminate all medical education that was not based on pharmaceutical intervention.\n\nHerbal medicine. Naturopathy. Homeopathy. Chiropractic. These were labelled as "quackery." Schools that taught these disciplines were systematically shut down or defunded. The remaining medical schools — those that taught pharmacology — received massive funding from a single source: John D. Rockefeller.\n\nRockefeller was not just the world\'s first billionaire. He was the controlling shareholder of Standard Oil, from which petrochemicals are derived — and petrochemicals are the foundation of synthetic pharmaceutical drugs.\n\nBy reshaping medical education to focus exclusively on pharmaceutical treatments, Rockefeller ensured that the dominant healthcare model would require the products his companies sold. He turned sickness into a market.\n\nBut it did not stop with medicine. The same infrastructure of institutional funding — Carnegie grants, Rockefeller endowments — shaped university curricula, public school systems, and the structure of academic research in ways that still operate today.\n\nThe world you live in was not designed by accident. It was designed by men who understood that whoever shapes the institutions shapes the people within them.',                                                                                                                        '307',   '2024-11-20', 1),
    (8,  'Water Is the Next Gold',                          'Awareness',     'The global water crisis is already here — and AI data centers consuming 800 billion litres daily are making it catastrophically worse.',                                                                                                      'Freshwater constitutes 2.5% of all water on earth. Of that 2.5%, roughly 69% is locked in glaciers and ice caps. Another 30% is in groundwater that is difficult to access. That leaves less than 1% of all water on earth readily available for human use.\n\nAnd we are running out of it faster than any previous point in human history.\n\nThe reasons are multiple and accelerating: population growth, industrial agriculture, climate change affecting rainfall patterns, and now — the newest and most alarming factor — artificial intelligence.\n\nAI training requires cooling infrastructure for massive data centres. A single AI data centre can consume billions of litres of water annually. Reports from 2023 indicate that training a single large language model uses approximately 700,000 litres of water. At scale, across thousands of facilities globally, estimates suggest AI infrastructure now consumes 800 billion litres of water annually. That number is projected to grow dramatically through 2030.\n\nWater wars are not a future scenario. They have already begun — quietly, in legal disputes over rivers, in diplomatic crises over dam projects, in the displacement of communities whose wells have run dry.\n\nPakistan, which depends heavily on glacial meltwater from the Himalayas and the Indus river system, is among the most water-stressed nations on earth. And the glaciers are melting faster than anyone predicted.',                                                                                                       '3.5K',  '2024-12-10', 1),
    (9,  '10,000 People — Why This Community Matters',     'Awareness',     'A message to the community that chose to wake up — and why each of you is part of something bigger.',                                                                                                                                         'When this channel reached 10,000 people, I stopped. I sat quietly with that number for a long time.\n\nTen thousand people is not a statistic. It is ten thousand individual human beings who, at some point, decided they wanted to understand the world more honestly. Ten thousand people who chose uncomfortable information over comfortable entertainment. Ten thousand people who, in a digital landscape designed to keep them distracted, chose to pay attention.\n\nThat is not ordinary.\n\nMost people, every day, are told what to consume, what to believe, what to fear, and what to want. The entire infrastructure of social media, advertising, and political communication is designed to manufacture consent — to make you feel like you are thinking freely while guiding you toward pre-approved conclusions.\n\nThe people who find their way to a channel like this one are the people who felt something was off. Who noticed the gaps between what they were told and what they observed. Who were willing, despite social pressure, despite discomfort, despite the very human desire to simply fit in — to keep asking questions.\n\nYou are not just viewers. You are a community of people who refused to stop asking. And a community like that changes things.\n\nNot immediately. Not all at once. But consistently, quietly, and powerfully — the way water shapes stone.',                                                                                                                                              '10K',   '2024-07-20', 0),
    (10, 'The PAK-Afghan War — What Really Happened',      'History',       'The untold history of a conflict that shaped an entire region and whose consequences are still unfolding.',                                                                                                                                    'The conflict between Pakistan and Afghanistan is older than either nation\'s modern form — but it has been deliberately misrepresented at every stage, in every direction, by every party that had something to gain from the misrepresentation.\n\nThe West presents it as a story of terrorism and state failure. Afghanistan presents it as Pakistani interference. Pakistan presents it as defensive action against cross-border militancy. Each narrative contains fragments of truth and enormous volumes of omission.\n\nWhat the official narratives carefully avoid is this: the conditions that created the Taliban were not organic. They were cultivated — by Cold War strategy, by regional intelligence competition, and by a deliberate policy of using religious militancy as a geopolitical instrument against the Soviet Union.\n\nThe United States, Pakistan\'s ISI, and Saudi Arabia formed a triangle of funding, training, and ideology that manufactured the Afghan Mujahideen in the 1980s. When the Soviets left, that infrastructure did not disappear. It evolved. The Taliban that emerged was, in significant part, a Frankenstein creature of Cold War architecture.\n\nPakistan then spent decades managing a monster it helped create — sometimes directing it, sometimes containing it, sometimes being attacked by it. The border regions — FATA, KP — became the human cost of this impossible position.\n\nThe people of both nations paid with their lives for decisions made in Washington, Riyadh, and Rawalpindi.',                                                                                                                        '24K',   '2024-10-05', 0),
   ]

SETTINGS_DEFAULTS = [
    ('password',   'BISMA2020'),
    ('tagline',    'Complex issues. Simple words. Uncomfortable truths.'),
    ('instagram',  'https://instagram.com/thecatvoice'),
    ('youtube',    'https://youtube.com/@thecatvoice-14?si=-2mHg3NkWpH34m6z'),
    ('email',      'thecatvoice13@gmail.com'),
    ('phone',      '+92 329 3487744'),
    ('followers',  '65K'),
    ('peak_views', '4.3M'),
    ('about_text', 'I am the voice for those who have been silenced. In a world where important conversations get buried, ignored, or twisted — I refuse to stay quiet. The Cat Voice was born from one simple belief: that every person deserves to understand the world they live in, no matter how complex, how hidden, or how uncomfortable the truth may be. I break down geopolitics, conspiracy theories, historical events, and social injustices — not for the few who already know, but for the many who deserve to know. Because awareness is not a privilege. It is a right. And yes — I am proudly an ailurophile. A cat lover at heart. Just like cats, I am quietly observant, fiercely independent, and I always land on my feet. That is exactly why The Cat Voice exists — watching, listening, and speaking when it matters most. But this is not just my journey — it is ours. Every view, every comment, every share tells me that you are here, you are listening, and you refuse to look away. We are not just viewers and a creator. We are one voice — standing together against silence.'),
]

def init_db():
    import os
    db_path = DATABASE
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS stories (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        title    TEXT NOT NULL,
        category TEXT NOT NULL,
        excerpt  TEXT,
        content  TEXT,
        views    TEXT,
        date     TEXT,
        featured INTEGER DEFAULT 0
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key   TEXT PRIMARY KEY,
        value TEXT
    )''')

    # Only seed stories if table is empty (first time setup)
    count = c.execute('SELECT COUNT(*) FROM stories').fetchone()[0]
    if count == 0:
        for s in STORIES:
            c.execute(
                'INSERT INTO stories (id, title, category, excerpt, content, views, date, featured) VALUES (?,?,?,?,?,?,?,?)',
                s
            )

    # Insert default settings only if they don't exist
    for key, value in SETTINGS_DEFAULTS:
        c.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (key, value))

    conn.commit()
    conn.close()

init_db()

# ──────────────────────────────────────────────
#  Authentication decorator
# ──────────────────────────────────────────────

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin'):
            flash('Please log in to access the admin panel.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

# ──────────────────────────────────────────────
#  Public Routes
# ──────────────────────────────────────────────

@app.route('/')
def home():
    settings = get_settings()
    featured = query_db('SELECT * FROM stories WHERE featured = 1 ORDER BY id DESC')
    all_stories = query_db('SELECT * FROM stories ORDER BY id DESC')
    total = query_db('SELECT COUNT(*) as cnt FROM stories', one=True)['cnt']
    return render_template('home.html',
                           settings=settings,
                           featured=featured,
                           all_stories=all_stories,
                           total_stories=total)

@app.route('/story/<int:story_id>')
def story(story_id):
    settings = get_settings()
    s = query_db('SELECT * FROM stories WHERE id = ?', [story_id], one=True)
    if s is None:
        return redirect(url_for('home'))
    related = query_db(
        'SELECT * FROM stories WHERE category = ? AND id != ? ORDER BY id DESC LIMIT 3',
        [s['category'], story_id]
    )
    # Increment view-tracking is display only; views are text strings
    return render_template('story.html', settings=settings, story=s, related=related)

@app.route('/category/<cat>')
def category(cat):
    settings = get_settings()
    stories = query_db('SELECT * FROM stories WHERE category = ? ORDER BY id DESC', [cat])
    return render_template('category.html', settings=settings, stories=stories, category=cat)

@app.route('/about')
def about():
    settings = get_settings()
    return render_template('about.html', settings=settings)

@app.route('/contact')
def contact():
    settings = get_settings()
    return render_template('contact.html', settings=settings)

# ──────────────────────────────────────────────
#  Admin Routes
# ──────────────────────────────────────────────

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin'):
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        password = request.form.get('password', '')
        settings = get_settings()
        if password == settings.get('password', 'BISMA2020'):
            session['admin'] = True
            flash('Welcome back, Bisma!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Incorrect password. Please try again.', 'error')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    settings = get_settings()
    stories = query_db('SELECT * FROM stories ORDER BY id DESC')
    total = query_db('SELECT COUNT(*) as cnt FROM stories', one=True)['cnt']
    featured_count = query_db('SELECT COUNT(*) as cnt FROM stories WHERE featured=1', one=True)['cnt']
    categories_count = query_db('SELECT COUNT(DISTINCT category) as cnt FROM stories', one=True)['cnt']
    return render_template('admin_dashboard.html',
                           settings=settings,
                           stories=stories,
                           total=total,
                           featured_count=featured_count,
                           categories_count=categories_count)

@app.route('/admin/add', methods=['GET', 'POST'])
@admin_required
def admin_add():
    settings = get_settings()
    if request.method == 'POST':
        title    = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        excerpt  = request.form.get('excerpt', '').strip()
        content  = request.form.get('content', '').strip()
        views    = request.form.get('views', '0').strip()
        date     = request.form.get('date', '').strip()
        featured = 1 if request.form.get('featured') else 0

        if not title or not category:
            flash('Title and Category are required.', 'error')
        else:
            execute_db(
                'INSERT INTO stories (title, category, excerpt, content, views, date, featured) VALUES (?,?,?,?,?,?,?)',
                (title, category, excerpt, content, views, date, featured)
            )
            flash(f'Story "{title}" added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
    return render_template('admin_form.html', settings=settings, story=None, action='Add')

@app.route('/admin/edit/<int:story_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit(story_id):
    settings = get_settings()
    s = query_db('SELECT * FROM stories WHERE id = ?', [story_id], one=True)
    if s is None:
        flash('Story not found.', 'error')
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        title    = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        excerpt  = request.form.get('excerpt', '').strip()
        content  = request.form.get('content', '').strip()
        views    = request.form.get('views', '0').strip()
        date     = request.form.get('date', '').strip()
        featured = 1 if request.form.get('featured') else 0

        if not title or not category:
            flash('Title and Category are required.', 'error')
        else:
            execute_db(
                'UPDATE stories SET title=?, category=?, excerpt=?, content=?, views=?, date=?, featured=? WHERE id=?',
                (title, category, excerpt, content, views, date, featured, story_id)
            )
            flash(f'Story "{title}" updated successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
    return render_template('admin_form.html', settings=settings, story=s, action='Edit')

@app.route('/admin/delete/<int:story_id>')
@admin_required
def admin_delete(story_id):
    s = query_db('SELECT title FROM stories WHERE id = ?', [story_id], one=True)
    if s:
        execute_db('DELETE FROM stories WHERE id = ?', [story_id])
        flash(f'Story "{s["title"]}" deleted.', 'success')
    else:
        flash('Story not found.', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/toggle_featured/<int:story_id>')
@admin_required
def admin_toggle_featured(story_id):
    s = query_db('SELECT title, featured FROM stories WHERE id = ?', [story_id], one=True)
    if s:
        new_val = 0 if s['featured'] else 1
        execute_db('UPDATE stories SET featured=? WHERE id=?', (new_val, story_id))
        status = 'featured' if new_val else 'unfeatured'
        flash(f'"{s["title"]}" is now {status}.', 'success')
    else:
        flash('Story not found.', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    settings = get_settings()
    if request.method == 'POST':
        keys = ['tagline', 'about_text', 'instagram', 'youtube', 'email', 'phone', 'followers', 'peak_views']
        for key in keys:
            value = request.form.get(key, '').strip()
            execute_db('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
        # Handle password change
        new_password = request.form.get('password', '').strip()
        if new_password:
            execute_db('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', ('password', new_password))
        flash('Settings saved successfully!', 'success')
        return redirect(url_for('admin_settings'))
    return render_template('admin_settings.html', settings=settings)

# ──────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True, port=5000)
