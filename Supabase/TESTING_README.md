# Testing Guide for Database Fixes

## 🎯 Quick Start (5 minutes)

### Step 1: Run SQL Migration (2 min)
1. Open Supabase Dashboard → SQL Editor
2. Copy SQL from the artifact "database_migration.sql"
3. Click **Run**
4. Verify success messages

### Step 2: Run Unit Tests (30 sec)
```bash
cd "C:\Users\ratho\Desktop\data analysis\clone_github\math_content_generator_agent"
python Supabase\test_database_fixes.py
```

Expected: **9/9 tests pass**

### Step 3: Run Integration Tests (60 sec)
```bash
python Supabase\test_integration.py
```

Expected: **All integration tests pass**

---

## 📂 Test Files Location

Save these files in `Supabase/` directory:
- `test_database_fixes.py` (unit tests)
- `test_integration.py` (integration tests)

Files are available in the Claude artifacts above.

---

## ✅ What's Being Tested

### Issue #1: Primary Key Usage
- Updates use `id` instead of `Question_Number`
- Deletes use `id` instead of `Question_Number`
- UNIQUE constraint on `Question_Number`

### Issue #2: Race Conditions
- Database sequence auto-generates `Question_Number`
- Sequential numbering without gaps
- Thread-safe concurrent insertions

### Issue #3: Question Type
- `question_type` column exists and is required
- Validation rejects invalid types
- All 3 types work: MCQ, Fill-in-the-Blank, Yes/No
- Filtering and counting by type works

---

## 🐛 Common Issues

**"column question_type does not exist"**
→ Run SQL migration script first

**"Question_Number cannot be null"**
→ Verify sequence default is set

**Connection errors**
→ Check `.env` file has correct credentials

---

## 📊 Success Criteria

✅ SQL migration completes without errors
✅ All 9 unit tests pass
✅ Integration tests complete successfully
✅ No duplicate Question_Numbers
✅ question_type validation works

---

## 🆘 Need Help?

See the complete "Testing Quick Start Checklist" artifact for:
- Detailed troubleshooting
- Manual testing examples
- Verification queries
- Expected outputs

All artifacts are available in the conversation above.
