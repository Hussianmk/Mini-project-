from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json, os, uuid
from datetime import datetime, date, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = 'ncc-army-wing-secret-2024'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')

# ─── data helpers ────────────────────────────────────────────────────────────
def load_data():
    if not os.path.exists(DATA_FILE):
        return seed_data()
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(d):
    with open(DATA_FILE, 'w') as f:
        json.dump(d, f, indent=2, default=str)

def seed_data():
    d = {
        "users": [
            {"id":"u1","username":"ano_sharma", "password":"ano123", "role":"ANO",   "name":"Lt. Rajiv Sharma",   "email":"sharma@ncc.in","cadet_id":None},
            {"id":"u2","username":"cc_rahul",   "password":"cc123",  "role":"CC",    "name":"Cdt Capt Rahul Dev", "email":"rahul@ncc.in", "cadet_id":None},
            {"id":"u3","username":"lc_priya",   "password":"lc123",  "role":"LC",    "name":"Ldg Cdt Priya Nair", "email":"priya@ncc.in", "cadet_id":"c3"},
            {"id":"u4","username":"cdt_arjun",  "password":"cdt123", "role":"Cadet", "name":"Cdt Arjun Mehta",    "email":"arjun@ncc.in", "cadet_id":"c1"},
            {"id":"u5","username":"cdt_sneha",  "password":"cdt123", "role":"Cadet", "name":"Cdt Sneha Patel",    "email":"sneha@ncc.in", "cadet_id":"c2"}
        ],
        "cadets": [
            {"id":"c1","name":"Arjun Mehta",   "service_number":"KAR/2024/001","rank":"Cadet",          "platoon":"Alpha",  "contact":"9876543210","email":"arjun@ncc.in",  "joined":"2024-01-15","blood_group":"O+"},
            {"id":"c2","name":"Sneha Patel",   "service_number":"KAR/2024/002","rank":"Lance Corporal", "platoon":"Alpha",  "contact":"9876543211","email":"sneha@ncc.in",  "joined":"2024-01-15","blood_group":"A+"},
            {"id":"c3","name":"Priya Nair",    "service_number":"KAR/2024/003","rank":"Corporal",       "platoon":"Bravo",  "contact":"9876543212","email":"priya@ncc.in",  "joined":"2024-01-15","blood_group":"B+"},
            {"id":"c4","name":"Vikram Singh",  "service_number":"KAR/2024/004","rank":"Sergeant",       "platoon":"Bravo",  "contact":"9876543213","email":"vikram@ncc.in", "joined":"2024-02-01","blood_group":"AB+"},
            {"id":"c5","name":"Ananya Reddy",  "service_number":"KAR/2024/005","rank":"Cadet",          "platoon":"Charlie","contact":"9876543214","email":"ananya@ncc.in", "joined":"2024-02-01","blood_group":"O-"},
            {"id":"c6","name":"Rohan Gupta",   "service_number":"KAR/2024/006","rank":"Cadet",          "platoon":"Charlie","contact":"9876543215","email":"rohan@ncc.in",  "joined":"2024-02-10","blood_group":"A-"},
            {"id":"c7","name":"Deepika Kumar", "service_number":"KAR/2024/007","rank":"Lance Corporal", "platoon":"Delta",  "contact":"9876543216","email":"deepika@ncc.in","joined":"2024-03-01","blood_group":"B-"},
            {"id":"c8","name":"Karan Joshi",   "service_number":"KAR/2024/008","rank":"Cadet",          "platoon":"Delta",  "contact":"9876543217","email":"karan@ncc.in",  "joined":"2024-03-01","blood_group":"O+"}
        ],
        "attendance": {},
        "announcements": [
            {"id":"ann1","title":"Annual Training Camp 2024","body":"Annual Training Camp scheduled 15-25 July 2024 at Dharwad. All cadets report by 0600 hrs in combat uniform.","author":"Lt. Rajiv Sharma","role":"ANO","date":"2024-06-01"},
            {"id":"ann2","title":"Saturday Parade – This Week","body":"Saturday parade is mandatory. Dress: SD Uniform. Time 0800 hrs sharp. Defaulters marked absent.","author":"Cdt Capt Rahul Dev","role":"CC","date":"2024-06-05"},
            {"id":"ann3","title":"Republic Day Contingent Selection","body":"Selection for Republic Day Parade contingent on 20 June 2024. Cadets with attendance >= 75% are eligible.","author":"Lt. Rajiv Sharma","role":"ANO","date":"2024-06-10"}
        ],
        "change_requests": []
    }
    save_data(d)
    return d

# ─── decorators ──────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({"error":"Unauthorized"}), 401
            return redirect(url_for('login_page'))
        return f(*a, **kw)
    return dec

def role_required(*roles):
    def wrap(f):
        @wraps(f)
        def dec(*a, **kw):
            if session.get('role') not in roles:
                return jsonify({"error":"Forbidden"}), 403
            return f(*a, **kw)
        return dec
    return wrap

# ─── pages ───────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return redirect(url_for('dashboard') if 'user_id' in session else url_for('login_page'))

@app.route('/login')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html')

# ─── auth api ────────────────────────────────────────────────────────────────
@app.route('/api/login', methods=['POST'])
def api_login():
    d    = load_data()
    body = request.get_json(force=True) or {}
    user = next((u for u in d['users']
                 if u['username'] == body.get('username','').strip()
                 and u['password'] == body.get('password','').strip()), None)
    if not user:
        return jsonify({"error":"Invalid username or password"}), 401
    session.permanent = True
    session['user_id']  = user['id']
    session['role']     = user['role']
    session['name']     = user['name']
    session['cadet_id'] = user.get('cadet_id')
    return jsonify({"ok":True,"role":user['role'],"name":user['name'],
                    "id":user['id'],"cadet_id":user.get('cadet_id')})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"ok":True})

@app.route('/api/session')
def api_session():
    if 'user_id' not in session:
        return jsonify({"logged_in":False})
    return jsonify({"logged_in":True,"role":session['role'],
                    "name":session['name'],"id":session['user_id'],
                    "cadet_id":session.get('cadet_id')})

# ─── dashboard stats ─────────────────────────────────────────────────────────
@app.route('/api/dashboard')
@login_required
def api_dashboard():
    d     = load_data()
    today = date.today().isoformat()
    total = len(d['cadets'])
    trec  = d['attendance'].get(today,{}).get('records',{})
    pres  = sum(1 for v in trec.values() if v=='P')
    dates = list(d['attendance'].keys())
    tp=ts=0
    for dt in dates:
        recs = d['attendance'][dt].get('records',{})
        ts  += len(recs)
        tp  += sum(1 for v in recs.values() if v=='P')
    avg = round((tp/ts*100) if ts else 0,1)
    pend = sum(1 for r in d['change_requests'] if r['status']=='pending')
    return jsonify({"total_cadets":total,"present_today":pres,"avg_pct":avg,
                    "active_users":len(d['users']),"sessions_held":len(dates),
                    "pending_requests":pend})

# ─── cadets ──────────────────────────────────────────────────────────────────
@app.route('/api/cadets', methods=['GET'])
@login_required
def get_cadets():
    d  = load_data()
    if session['role']=='Cadet' and session.get('cadet_id'):
        return jsonify([c for c in d['cadets'] if c['id']==session['cadet_id']])
    return jsonify(d['cadets'])

@app.route('/api/cadets', methods=['POST'])
@login_required
@role_required('ANO','CC')
def add_cadet():
    d    = load_data()
    body = request.get_json(force=True) or {}
    if not body.get('name') or not body.get('service_number'):
        return jsonify({"error":"Name and service number required"}), 400
    c = {"id":'c_'+uuid.uuid4().hex[:8],
         "name":body.get('name','').strip(),
         "service_number":body.get('service_number','').strip(),
         "rank":body.get('rank','Cadet'),
         "platoon":body.get('platoon','Alpha'),
         "contact":body.get('contact','').strip(),
         "email":body.get('email','').strip(),
         "joined":body.get('joined',date.today().isoformat()),
         "blood_group":body.get('blood_group','').strip()}
    d['cadets'].append(c)
    save_data(d)
    return jsonify(c), 201

@app.route('/api/cadets/<cid>', methods=['PUT'])
@login_required
@role_required('ANO','CC')
def update_cadet(cid):
    d    = load_data()
    body = request.get_json(force=True) or {}
    for i,c in enumerate(d['cadets']):
        if c['id']==cid:
            for k in ['name','service_number','rank','platoon','contact','email','joined','blood_group']:
                if k in body: d['cadets'][i][k]=body[k]
            save_data(d)
            return jsonify(d['cadets'][i])
    return jsonify({"error":"Not found"}), 404

@app.route('/api/cadets/<cid>', methods=['DELETE'])
@login_required
@role_required('ANO')
def delete_cadet(cid):
    d = load_data()
    before = len(d['cadets'])
    d['cadets'] = [c for c in d['cadets'] if c['id']!=cid]
    if len(d['cadets'])==before:
        return jsonify({"error":"Not found"}), 404
    save_data(d)
    return jsonify({"ok":True})

# ─── attendance ───────────────────────────────────────────────────────────────
@app.route('/api/attendance/<att_date>', methods=['GET'])
@login_required
def get_att(att_date):
    d = load_data()
    return jsonify(d['attendance'].get(att_date,{"records":{},"frozen":False}))

@app.route('/api/attendance/<att_date>', methods=['POST'])
@login_required
@role_required('ANO','CC')
def save_att(att_date):
    d    = load_data()
    body = request.get_json(force=True) or {}
    ex   = d['attendance'].get(att_date,{"records":{},"frozen":False})
    if ex.get('frozen') and session['role']!='ANO':
        return jsonify({"error":"Attendance frozen"}), 403
    ex['records'] = body.get('records', ex['records'])
    d['attendance'][att_date] = ex
    save_data(d)
    return jsonify(ex)

@app.route('/api/attendance/<att_date>/submit', methods=['POST'])
@login_required
@role_required('ANO','CC')
def submit_att(att_date):
    d    = load_data()
    body = request.get_json(force=True) or {}
    entry = {"records":body.get('records',{}),"frozen":True,
             "submitted_by":session['name'],"submitted_at":datetime.now().isoformat()}
    d['attendance'][att_date] = entry
    save_data(d)
    return jsonify(entry)

@app.route('/api/attendance/<att_date>/unfreeze', methods=['POST'])
@login_required
@role_required('ANO')
def unfreeze_att(att_date):
    d = load_data()
    if att_date in d['attendance']:
        d['attendance'][att_date]['frozen'] = False
        save_data(d)
    return jsonify({"ok":True})

@app.route('/api/attendance/report')
@login_required
def att_report():
    d      = load_data()
    cadets = d['cadets']
    if session['role']=='Cadet' and session.get('cadet_id'):
        cadets = [c for c in cadets if c['id']==session['cadet_id']]
    dates  = sorted(d['attendance'].keys())
    report = []
    for c in cadets:
        row = {"cadet":c,"records":{},"present":0,"absent":0,"leave":0,"total":0}
        for dt in dates:
            rec = d['attendance'][dt].get('records',{}).get(c['id'])
            row['records'][dt] = rec if rec else '-'
            if rec in ('P','A','L'):
                row['total']+=1
                if rec=='P': row['present']+=1
                elif rec=='A': row['absent']+=1
                elif rec=='L': row['leave']+=1
        row['pct'] = round((row['present']/row['total']*100) if row['total'] else 0,1)
        report.append(row)
    return jsonify({"report":report,"dates":dates})

# ─── announcements ────────────────────────────────────────────────────────────
@app.route('/api/announcements', methods=['GET'])
@login_required
def get_anns():
    d = load_data()
    return jsonify(sorted(d['announcements'],key=lambda x:x['date'],reverse=True))

@app.route('/api/announcements', methods=['POST'])
@login_required
@role_required('ANO','CC')
def add_ann():
    d    = load_data()
    body = request.get_json(force=True) or {}
    if not body.get('title') or not body.get('body'):
        return jsonify({"error":"Title and body required"}), 400
    ann = {"id":'ann_'+uuid.uuid4().hex[:8],"title":body['title'].strip(),
           "body":body['body'].strip(),"author":session['name'],
           "role":session['role'],"date":date.today().isoformat()}
    d['announcements'].insert(0,ann)
    save_data(d)
    return jsonify(ann), 201

@app.route('/api/announcements/<aid>', methods=['DELETE'])
@login_required
@role_required('ANO','CC')
def del_ann(aid):
    d = load_data()
    d['announcements'] = [a for a in d['announcements'] if a['id']!=aid]
    save_data(d)
    return jsonify({"ok":True})

# ─── users ────────────────────────────────────────────────────────────────────
@app.route('/api/users', methods=['GET'])
@login_required
@role_required('ANO')
def get_users():
    d = load_data()
    return jsonify([{k:v for k,v in u.items() if k!='password'} for u in d['users']])

@app.route('/api/users', methods=['POST'])
@login_required
@role_required('ANO')
def add_user():
    d    = load_data()
    body = request.get_json(force=True) or {}
    if not body.get('username') or not body.get('password'):
        return jsonify({"error":"Username and password required"}), 400
    if any(u['username']==body['username'] for u in d['users']):
        return jsonify({"error":"Username already exists"}), 409
    u = {"id":'u_'+uuid.uuid4().hex[:8],"username":body['username'].strip(),
         "password":body['password'],"role":body.get('role','Cadet'),
         "name":body.get('name','').strip(),"email":body.get('email','').strip(),
         "cadet_id":body.get('cadet_id') or None}
    d['users'].append(u)
    save_data(d)
    return jsonify({k:v for k,v in u.items() if k!='password'}), 201

@app.route('/api/users/<uid>', methods=['PUT'])
@login_required
@role_required('ANO')
def update_user(uid):
    d    = load_data()
    body = request.get_json(force=True) or {}
    for i,u in enumerate(d['users']):
        if u['id']==uid:
            # NOTE: session stays alive even when credentials change — by design
            for k in ['role','name','email','cadet_id','username','password']:
                if k in body:
                    d['users'][i][k] = body[k]
            save_data(d)
            return jsonify({k:v for k,v in d['users'][i].items() if k!='password'})
    return jsonify({"error":"Not found"}), 404

@app.route('/api/users/<uid>', methods=['DELETE'])
@login_required
@role_required('ANO')
def delete_user(uid):
    if uid==session['user_id']:
        return jsonify({"error":"Cannot delete your own account"}), 400
    d = load_data()
    before = len(d['users'])
    d['users'] = [u for u in d['users'] if u['id']!=uid]
    if len(d['users'])==before:
        return jsonify({"error":"Not found"}), 404
    save_data(d)
    return jsonify({"ok":True})

@app.route('/api/users/<uid>/reset-password', methods=['POST'])
@login_required
@role_required('ANO')
def reset_pwd(uid):
    d    = load_data()
    body = request.get_json(force=True) or {}
    pwd  = body.get('password','').strip()
    if not pwd:
        return jsonify({"error":"Password required"}), 400
    for i,u in enumerate(d['users']):
        if u['id']==uid:
            # NOTE: session of that user stays alive — no forced logout by design
            d['users'][i]['password'] = pwd
            save_data(d)
            return jsonify({"ok":True})
    return jsonify({"error":"Not found"}), 404

# ─── change requests ──────────────────────────────────────────────────────────
@app.route('/api/change-requests', methods=['GET'])
@login_required
@role_required('ANO','CC')
def get_cr():
    d    = load_data()
    reqs = d['change_requests']
    if session['role']=='CC':
        reqs = [r for r in reqs if r.get('requested_by_id')==session['user_id']]
    return jsonify(sorted(reqs,key=lambda x:x.get('created_at',''),reverse=True))

@app.route('/api/change-requests', methods=['POST'])
@login_required
@role_required('CC')
def create_cr():
    d    = load_data()
    body = request.get_json(force=True) or {}
    req  = {"id":'cr_'+uuid.uuid4().hex[:8],"status":"pending",
            "cadet_id":body.get('cadet_id',''),"cadet_name":body.get('cadet_name',''),
            "date":body.get('date',''),"old_status":body.get('old_status','-'),
            "new_status":body.get('new_status','P'),"reason":body.get('reason','').strip(),
            "requested_by":session['name'],"requested_by_id":session['user_id'],
            "created_at":datetime.now().isoformat(),"reviewed_at":None,"rejection_note":None}
    d['change_requests'].append(req)
    save_data(d)
    return jsonify(req), 201

@app.route('/api/change-requests/<rid>/approve', methods=['POST'])
@login_required
@role_required('ANO')
def approve_cr(rid):
    d = load_data()
    for i,r in enumerate(d['change_requests']):
        if r['id']==rid:
            d['change_requests'][i]['status']      = 'approved'
            d['change_requests'][i]['reviewed_at'] = datetime.now().isoformat()
            att = r['date']
            if att in d['attendance']:
                d['attendance'][att]['records'][r['cadet_id']] = r['new_status']
            save_data(d)
            return jsonify({"ok":True})
    return jsonify({"error":"Not found"}), 404

@app.route('/api/change-requests/<rid>/reject', methods=['POST'])
@login_required
@role_required('ANO')
def reject_cr(rid):
    d    = load_data()
    body = request.get_json(force=True) or {}
    for i,r in enumerate(d['change_requests']):
        if r['id']==rid:
            d['change_requests'][i]['status']        = 'rejected'
            d['change_requests'][i]['reviewed_at']   = datetime.now().isoformat()
            d['change_requests'][i]['rejection_note']= body.get('note','').strip()
            save_data(d)
            return jsonify({"ok":True})
    return jsonify({"error":"Not found"}), 404

@app.route('/api/change-requests/pending-count')
@login_required
def pending_count():
    d = load_data()
    return jsonify({"count":sum(1 for r in d['change_requests'] if r['status']=='pending')})

# ─── run ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    if not os.path.exists(DATA_FILE):
        seed_data()
        print("✓ Demo data created")
    print("\n" + "="*48)
    print("  NCC PORTAL — Army Wing")
    print("  Open: http://127.0.0.1:5000")
    print("="*48)
    print("  ano_sharma / ano123  (ANO)")
    print("  cc_rahul   / cc123   (CC)")
    print("  lc_priya   / lc123   (LC)")
    print("  cdt_arjun  / cdt123  (Cadet)")
    print("="*48 + "\n")
    app.run(debug=True, port=5000)
