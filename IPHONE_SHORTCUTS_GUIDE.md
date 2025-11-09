# iPhone Shortcuts for Pi Zero Medicine Tracker

Complete guide to creating iPhone Shortcuts for medicine tracking.

---

## New API Endpoints ✨

### 1. **GET /api/medicine/pending**
Get medicines due now (within time window)

### 2. **POST /api/medicine/mark-taken**
Mark medicines as taken and decrement pill count

---

## Quick Start: Create Your First Shortcut

### Shortcut 1: "What Medicines Are Due?"

**Purpose:** Check what medicines you need to take right now

**Steps:**
1. Open **Shortcuts** app on iPhone
2. Tap **+** (New Shortcut)
3. Add action: **Get Contents of URL**
   - URL: `http://192.168.50.202:5000/api/medicine/pending`
   - Method: GET
4. Add action: **Get Dictionary from Input**
5. Add action: **Get Value for Key** `count` in Dictionary
6. Add action: **If** Count > 0
   - **Then:**
     - Add action: **Get Value for Key** `medicines` in Dictionary
     - Add action: **Repeat with Each** item in Medicines
       - Add action: **Get Dictionary Value** → Key: `name` from Repeat Item
       - Add action: **Get Dictionary Value** → Key: `dosage` from Repeat Item
       - Add action: **Show Notification**
         - Title: "Take Medicine"
         - Body: "{{Name}} - {{Dosage}}"
     - End Repeat
   - **Otherwise:**
     - Add action: **Show Notification**
       - Title: "All Clear!"
       - Body: "No medicines due right now"
7. Name it: **"Check My Meds"**
8. Done!

---

### Shortcut 2: "I Took My Medicine"

**Purpose:** Mark medicine(s) as taken with one tap

**Steps:**
1. Open **Shortcuts** app
2. Tap **+** (New Shortcut)
3. Add action: **Get Contents of URL**
   - URL: `http://192.168.50.202:5000/api/medicine/pending`
   - Method: GET
4. Add action: **Get Dictionary from Input**
5. Add action: **Get Value for Key** `medicines`
6. Add action: **Choose from List** → Medicines
   - **Prompt:** "Which medicine did you take?"
   - **Select Multiple:** YES (to mark multiple at once)
7. Add action: **Get Dictionary Value** → Key: `id` from Chosen Item
8. Add action: **Text** → `{"medicine_ids": [{{Dictionary Value}}]}`
9. Add action: **Get Contents of URL**
   - URL: `http://192.168.50.202:5000/api/medicine/mark-taken`
   - Method: POST
   - Request Body: JSON (from Text)
   - Headers: `Content-Type: application/json`
10. Add action: **Get Dictionary from Input**
11. Add action: **Get Value for Key** `message`
12. Add action: **Show Notification**
    - Title: "Medicine Marked"
    - Body: Dictionary Value
13. Name it: **"I Took My Meds"**
14. Done!

---

## Advanced Shortcuts

### Shortcut 3: "Morning Medicine Routine"

**Purpose:** Automatic morning medicine reminder

**Steps:**
1. Create new Shortcut
2. Add action: **Get Contents of URL**
   - URL: `http://192.168.50.202:5000/api/medicine/pending`
3. Add action: **Get Dictionary from Input**
4. Add action: **Get Value for Key** `count`
5. Add action: **If** Count > 0
   - Add action: **Get Value for Key** `medicines`
   - Add action: **Text**
     ```
     Good morning! Time to take:

     {{medicines}}
     ```
   - Add action: **Show Alert**
     - Title: "Morning Medicines"
     - Message: Text
     - Show Cancel Button: NO
   - Add action: **Ask for Input**
     - Prompt: "Did you take them?"
     - Input Type: Text
     - Default: "Yes"
   - Add action: **If** Provided Input = "Yes"
     - Add action: **Get Contents of URL**
       - URL: `http://192.168.50.202:5000/api/medicine/mark-taken`
       - Method: POST
       - Body: `{"medicine_ids": ["med_001", "med_1762467778545", "med_1762467794570"]}`
6. Set **Automation**:
   - Time of Day: 8:00 AM
   - Run Automatically: YES

---

### Shortcut 4: "Quick Mark - Vyvanse"

**Purpose:** One-tap to mark specific medicine (no menus)

**Steps:**
1. Create new Shortcut
2. Add action: **Get Contents of URL**
   - URL: `http://192.168.50.202:5000/api/medicine/mark-taken`
   - Method: POST
   - Request Body: JSON
   ```json
   {
     "medicine_id": "med_1762467778545"
   }
   ```
   - Headers: `Content-Type: application/json`
3. Add action: **Get Dictionary from Input**
4. Add action: **Get Value for Key** `pills_remaining` → from key `marked` → first item
5. Add action: **Show Notification**
   - Title: "Vyvanse Marked ✓"
   - Body: "{{Pills Remaining}} pills left"
6. Name it: **"Took Vyvanse"**
7. Add to Home Screen widget for 1-tap access!

---

### Shortcut 5: "Reorder Alert"

**Purpose:** Get list of medicines with low stock

**Steps:**
1. Create new Shortcut
2. Add action: **Get Contents of URL**
   - URL: `http://192.168.50.202:5000/api/medicine/data`
3. Add action: **Get Dictionary from Input**
4. Add action: **Get Value for Key** `medicines`
5. Add action: **Filter** Medicines
   - Where: `pills_remaining` ≤ `low_stock_threshold`
6. Add action: **If** Filter Results > 0
   - Add action: **Repeat with Each** item
     - Add action: **Text**
       ```
       {{Repeat Item.name}}: {{Repeat Item.pills_remaining}} pills
       ```
   - Add action: **Combine Text** with New Lines
   - Add action: **Show Alert**
     - Title: "⚠️ Reorder Needed"
     - Message: Combined Text
7. Name it: **"Check Stock"**

---

## API Reference for Shortcuts

### GET /api/medicine/pending

**Returns:** Medicines due now

```json
{
  "success": true,
  "count": 2,
  "medicines": [
    {
      "id": "med_001",
      "name": "Vitamin D",
      "dosage": "2000 IU",
      "time_window": "morning",
      "with_food": true,
      "notes": "Take with breakfast",
      "pills_remaining": 59,
      "low_stock": false
    }
  ],
  "checked_at": "2025-11-07T08:30:00"
}
```

---

### POST /api/medicine/mark-taken

**Request:**

**Single medicine:**
```json
{
  "medicine_id": "med_001"
}
```

**Multiple medicines:**
```json
{
  "medicine_ids": ["med_001", "med_002", "med_003"]
}
```

**With custom timestamp:**
```json
{
  "medicine_id": "med_001",
  "timestamp": "2025-11-07T08:30:00"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Marked 1 medicine(s) as taken",
  "marked": [
    {
      "id": "med_001",
      "name": "Vitamin D",
      "pills_remaining": 59,
      "low_stock": false
    }
  ],
  "timestamp": "2025-11-07T08:30:00"
}
```

---

### GET /api/medicine/data

**Returns:** All medicines and tracking data

```json
{
  "medicines": [...],
  "tracking": {...},
  "time_windows": {...}
}
```

---

## Tips & Tricks

### 1. **Add to Home Screen**
Make shortcuts accessible with widgets:
- Long press Home Screen → **+** → **Shortcuts**
- Add medium/large widget
- Select your medicine shortcuts

### 2. **Siri Integration**
All shortcuts work with Siri:
- "Hey Siri, check my meds"
- "Hey Siri, I took my meds"
- "Hey Siri, took Vyvanse"

### 3. **Automation Ideas**
- **Time-based:** 8 AM reminder every day
- **Location-based:** Remind when arriving home
- **NFC Tag:** Tap medicine bottle to mark taken
- **Apple Watch:** Quick mark from wrist

### 4. **Notification Settings**
Go to Settings → Shortcuts → enable:
- Allow Notifications
- Show on Lock Screen
- Badge App Icon

---

## Example: Complete "Mark All Morning Meds" Shortcut

**Detailed steps with screenshots alternative:**

```
1. Get Contents of URL
   └─ URL: http://192.168.50.202:5000/api/medicine/pending
   └─ Method: GET

2. Get Dictionary from "Contents of URL"

3. Get Value for "medicines" in Dictionary

4. Repeat with each item in "Dictionary Value"
   ├─ Get "id" from "Repeat Item"
   └─ Set Variable "MedIDs" to "Dictionary Value"

5. Get Contents of URL
   ├─ URL: http://192.168.50.202:5000/api/medicine/mark-taken
   ├─ Method: POST
   ├─ Headers: {"Content-Type": "application/json"}
   └─ Request Body: {"medicine_ids": [MedIDs]}

6. Get Dictionary from "Contents of URL"

7. Get Value for "message" in Dictionary

8. Show Notification
   ├─ Title: "Medicine Marked"
   └─ Body: "Dictionary Value"
```

---

## Troubleshooting

### "Could not connect to server"
- Check WiFi connection (must be on same network as Pi)
- Verify Pi IP: `192.168.50.202`
- Test in browser: http://192.168.50.202:5000

### "Invalid JSON"
- Use **Text** action to build JSON
- Ensure quotes around strings
- Use **Get Dictionary Value** instead of hardcoding

### "Medicine not found"
- Get medicine IDs from `/api/medicine/data`
- Copy exact ID (e.g., "med_1762467778545")
- Check medicine is `active: true`

### Shortcut doesn't run automatically
- Go to Automations tab
- Ensure "Run Immediately" is ON
- Check "Ask Before Running" is OFF

---

## Testing Commands (Terminal)

```bash
# Get pending medicines
curl http://192.168.50.202:5000/api/medicine/pending

# Mark medicine taken (single)
curl -X POST http://192.168.50.202:5000/api/medicine/mark-taken \
  -H "Content-Type: application/json" \
  -d '{"medicine_id": "med_001"}'

# Mark multiple medicines
curl -X POST http://192.168.50.202:5000/api/medicine/mark-taken \
  -H "Content-Type: application/json" \
  -d '{"medicine_ids": ["med_001", "med_1762467778545"]}'

# Get all medicines
curl http://192.168.50.202:5000/api/medicine/data
```

---

## Advanced: Using with Other Apps

### **Scriptable** (iOS automation)
```javascript
let url = "http://192.168.50.202:5000/api/medicine/pending";
let req = new Request(url);
let json = await req.loadJSON();

if (json.count > 0) {
  let notification = new Notification();
  notification.title = "Medicine Reminder";
  notification.body = json.medicines.map(m => m.name).join(", ");
  notification.schedule();
}
```

### **Drafts** (text automation)
Use URL scheme to mark medicines from notes.

### **IFTTT** (web automation)
- Trigger: Time (8:00 AM)
- Action: Webhook POST to mark-taken API

---

## Security Note

⚠️ **Important:** These APIs are currently **unauthenticated** and accessible to anyone on your local network.

For production use, consider:
1. VPN access only
2. API key authentication
3. HTTPS with valid certificate
4. IP whitelist

---

## Quick Reference Card

| Shortcut | Purpose | Method | Endpoint |
|----------|---------|--------|----------|
| Check Meds | See what's due | GET | `/api/medicine/pending` |
| Mark Taken | Record dose | POST | `/api/medicine/mark-taken` |
| Low Stock | Check inventory | GET | `/api/medicine/data` |

**Base URL:** `http://192.168.50.202:5000`

---

## Support

**API Documentation:** http://192.168.50.202:5000/api/
**Full Docs:** See PIZERO_MEDICINE_TRACKER_DOCUMENTATION.md

---

**Created:** November 7, 2025
**Version:** 1.0
