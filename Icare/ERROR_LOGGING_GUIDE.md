# CSV Upload - Error Logging Guide

## How to Check Console Errors

### Open Browser Console

**Chrome/Edge/Firefox:**
1. Press `F12` (or `Ctrl+Shift+I`)
2. Click the "Console" tab
3. You'll see all debug logs and errors

**Safari:**
1. Press `Cmd+Option+I`
2. Click "Console"

---

## What You'll See in Console

### Successful Upload (All Green ✓)
```
✓ Dashboard script loaded
Elements: {dropZone, csvFile, fileName, browseButton, uploadForm}
Drop zone clicked - triggering file input
File selected via input: {name: 'test_sample.csv', size: 1245}
Form submission started
Submitting file: {name: 'test_sample.csv', size: 1245}
Form data: {patient_name: '', details: '', csv_file: 'test_sample.csv'}
✓ Form submitted successfully
```

### Upload Failed (Red ❌)
```
❌ No file selected
❌ Invalid file type: application/json
❌ File too large: 15728640 bytes
```

---

## Backend Logs in Server Terminal

When you run Django, you'll see upload progress:

```
[UPLOAD] User test@example.com attempting upload. Files: ['csv_file']
[UPLOAD] File received: test_sample.csv (1245 bytes)
[UPLOAD] Parsing CSV file...
[UPLOAD] ✓ Parsed 10 records
[UPLOAD] CSV columns: ['age', 'gender', 'blood_pressure', 'cholesterol', 'glucose']
[UPLOAD] First record: {'age': '45', 'gender': 'Male', ...}
[UPLOAD] Processing 10 medical records for user test@example.com
[UPLOAD] Creating MedicalReport...
[UPLOAD] ✓ Medical report saved with ID: 5
[UPLOAD] Starting disease prediction...
[UPLOAD] ✓ Prediction complete: 15 diseases
[UPLOAD] Creating AnalysisResult...
[UPLOAD] ✓ Analysis result saved with ID: 3
[UPLOAD] ✓✓✓ SUCCESS: CSV uploaded and analyzed by test@example.com
```

---

## Errors You Might See

### File-Related Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `No file selected` | Didn't select a file | Click Browse or drag file |
| `Invalid file type` | Wrong file format | Use `.csv` format |
| `File too large` | File >10MB | Use smaller CSV file |
| `Empty CSV file` | No data rows | Add at least 1 data row |

### Parsing Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Error parsing CSV` | Invalid CSV format | Check format: age,gender,blood_pressure,cholesterol,glucose |
| `UnicodeDecodeError` | Invalid encoding | Save CSV as UTF-8 |
| `KeyError` | Missing columns | Ensure columns match required fields |

### Server Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Error saving report` | Database issue | Verify database is running |
| `Error in prediction` | ML model error | Check disease_predictor.py |
| `Error saving results` | Database issue | Check disk space |

---

## Check Django Logs

To see server-side logs, check where Django is running:

### If Running Terminal:
```
cd "c:\Users\shahal Muhammed\OneDrive\Documents\GitHub\icare\Icare"
python manage.py runserver
```

Logs appear in this terminal as you upload.

### Enable Detailed Logging

To save logs to a file, add to `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'DEBUG',
    },
}
```

Then check `debug.log` in project root.

---

## Step-by-Step Debug Process

### 1. Open Console (F12)
See what happens on client side

### 2. Try Upload
Watch for JavaScript errors

### 3. Check Server Terminal
Look for `[UPLOAD]` logs

### 4. If Error Appears
Read the error message carefully:
- `[UPLOAD ERROR]` = Something failed
- `[UPLOAD] ✓` = Step successful
- `[UPLOAD] ✓✓✓ SUCCESS` = Fully complete

### 5. Report the Error
If stuck, provide:
- Console error message
- Server log message
- File you tried to upload
- What column headers you used

---

## Common Issues & Fixes

### "File selected but nothing happens"
```
Check Console:
1. ✓ Form submission started
2. ❌ No file selected? → Select file again
3. If it says file is selected, check server logs
```

### "Upload takes forever"
```
Django is processing. Check server terminal:
- [UPLOAD] ✓ Parsed 10 records ← Parsing
- [UPLOAD] Creating MedicalReport... ← Database save
- [UPLOAD] Starting disease prediction... ← ML running
- Wait for ✓✓✓ SUCCESS
```

### "Chart doesn't show after upload"
```
Console should show:
- No JavaScript errors
- Form submission successful
- Check Network tab (F12 → Network)
  - POST request should be 200 OK
  - Response should contain results
```

---

## Test Upload

### Ready to Test?

1. **Open Browser Console:** F12
2. **Go to Dashboard:** http://localhost:8000/dashboard/
3. **Select Test File:** `test_sample.csv`
4. **Click Upload:** "Analyze Report"
5. **Watch Console:** See all logs appear
6. **Check Results:** Charts should appear in 1 second

### Expected Console Output:
```
✓ Dashboard script loaded
✓ File selected via input: {name: 'test_sample.csv', size: 1245}
✓ Form submission started
✓ Form submitted successfully
[Page reloads with results]
```

---

**Everything working? Great! 🎉**
**Errors? Check console and server logs!**
