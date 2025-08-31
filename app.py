from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import sqlite3
from google_analytics import get_google_analytics_data

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database setup
DB_NAME = 'analytics.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS page_views (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        page TEXT,
        session_id TEXT,
        timestamp DATETIME
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        start_time DATETIME,
        end_time DATETIME
    )''')
    conn.commit()
    conn.close()

init_db()

# Helper functions

def log_page_view(page):
    session_id = session.get('session_id')
    if not session_id:
        session_id = str(datetime.now().timestamp()) + str(request.remote_addr)
        session['session_id'] = session_id
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('INSERT INTO sessions (session_id, start_time) VALUES (?, ?)', (session_id, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO page_views (page, session_id, timestamp) VALUES (?, ?, ?)', (page, session_id, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def end_session():
    pass  # Removed to avoid using session outside request context

@app.route('/')
def home():
    log_page_view('home')
    return render_template('home_new.html')

@app.route('/about')
def about():
    log_page_view('about')
    return render_template('about_new.html')

@app.route('/services')
def services():
    log_page_view('services')
    return render_template('services_new.html')

@app.route('/contact')
def contact():
    log_page_view('contact')
    return render_template('contact_new.html')

@app.route('/dashboard')
def dashboard():
    try:
        # Get Google Analytics data
        ga_data = get_google_analytics_data()
        
        # Get local analytics data
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        # Page views
        c.execute('SELECT page, COUNT(*) FROM page_views GROUP BY page')
        local_page_views = c.fetchall()
        # Most visited pages
        c.execute('SELECT page, COUNT(*) as cnt FROM page_views GROUP BY page ORDER BY cnt DESC LIMIT 5')
        local_most_visited = c.fetchall()
        # Sessions
        c.execute('SELECT start_time, end_time FROM sessions')
        sessions = c.fetchall()
        total_sessions = len(sessions)
        bounce_count = 0
        total_duration = 0
        for s in sessions:
            start, end = s
            if not end:
                end = datetime.now().isoformat()
            try:
                duration = (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds()
            except Exception:
                duration = 0
            total_duration += duration
        # Bounce rate: sessions with only one page view
        c.execute('SELECT session_id, COUNT(*) FROM page_views GROUP BY session_id')
        session_views = c.fetchall()
        for sv in session_views:
            if sv[1] == 1:
                bounce_count += 1
        local_bounce_rate = (bounce_count / total_sessions * 100) if total_sessions else 0
        local_avg_session_duration = (total_duration / total_sessions) if total_sessions else 0
        conn.close()
        
        # Combine Google Analytics and local data
        # Use GA data if available, otherwise fall back to local data
        if ga_data['is_live_data']:
            # Use Google Analytics data as primary
            page_views = ga_data['page_views']
            most_visited = ga_data['page_views'][:5]
            bounce_rate = ga_data['metrics']['bounce_rate']
            avg_session_duration = ga_data['metrics']['avg_session_duration']
            total_sessions = ga_data['metrics']['total_sessions']
            active_users = ga_data['metrics']['active_users']
            total_page_views = ga_data['metrics']['page_views']
            real_time_users = ga_data['real_time_users']
            top_events = ga_data['top_events']
        else:
            # Use local analytics data
            page_views = local_page_views
            most_visited = local_most_visited
            bounce_rate = local_bounce_rate
            avg_session_duration = local_avg_session_duration
            total_sessions = total_sessions
            active_users = total_sessions  # Approximate
            total_page_views = sum(pv[1] for pv in page_views) if page_views else 0
            real_time_users = 0
            top_events = []
        
        return render_template('dashboard_new.html', 
                             page_views=page_views,
                             most_visited=most_visited,
                             bounce_rate=bounce_rate,
                             avg_session_duration=avg_session_duration,
                             total_sessions=total_sessions,
                             active_users=active_users,
                             total_page_views=total_page_views,
                             real_time_users=real_time_users,
                             top_events=top_events,
                             is_live_data=ga_data['is_live_data'],
                             ga_data=ga_data)
    except Exception as e:
        print(f"Dashboard error: {e}")
        return render_template('dashboard_new.html', 
                             page_views=[],
                             most_visited=[],
                             bounce_rate=0,
                             avg_session_duration=0,
                             total_sessions=0,
                             active_users=0,
                             total_page_views=0,
                             real_time_users=0,
                             top_events=[],
                             is_live_data=False,
                             ga_data={})

# Removed teardown_appcontext to avoid session access outside request context

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
