# NCC Portal – Army Wing

## Run in VS Code (3 steps)

**Step 1 — Open terminal in VS Code**
```
Terminal → New Terminal
```

**Step 2 — Install Flask**
```
pip install flask
```

**Step 3 — Run the app**
```
python app.py
```

Then open your browser at: **http://127.0.0.1:5000**

---

## Login Credentials

| Role | Username | Password |
|------|----------|----------|
| ANO (Admin) | `ano_sharma` | `ano123` |
| Cadet Captain | `cc_rahul` | `cc123` |
| Leading Cadet | `lc_priya` | `lc123` |
| Cadet | `cdt_arjun` | `cdt123` |

---

## Notes
- All data is saved to `data.json` automatically (created on first run)
- Changing a user's password or username does NOT log them out — session stays active by design
- Only the Logout button ends a session
