# Quick Start Guide - Optimized Google Maps Scraper

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Prepare Your URLs

Create or use an existing `urls.txt` file with Google Maps place URLs:

```
https://www.google.com/maps/place/.../@-33.8670,151.2093,17z
https://www.google.com/maps/place/.../@51.5074,-0.1278,17z
```

### 3. Run the Scraper

**Simple (2 parallel workers, 50 reviews per place):**
```bash
python scraper.py --i urls.txt --N 50 --workers 2
```

**Output will be saved to:** `data/output.csv`

---

## ⚡ Speed & Performance Tips

### For Maximum Speed (Risky)
```bash
python scraper.py --i urls.txt --N 100 --workers 3
```
- ⚠️ Higher chance of getting blocked
- Use only with caution or small batches
- Consider using a VPN

### For Reliable, Sustained Speed
```bash
python scraper.py --i urls.txt --N 100 --workers 2
```
- ✓ Best balance of speed and safety
- **Recommended for production use**

### For Testing / Debugging
```bash
python scraper.py --i urls.txt --N 10 --workers 1 --debug
```
- Shows browser window
- Use 1 worker for debugging
- Good for testing new URLs

---

## 📊 What's Optimized

✅ **Parallel Processing**: 2-4 URLs scraped simultaneously  
✅ **Anti-Detection**: User agent rotation, randomized delays, human-like behavior  
✅ **Performance**: Disabled images, headless mode, optimized page loads  
✅ **Smart Delays**: 0.5-2s scrolls, 0.8-2s clicks, 3-6s page loads  
✅ **Thread-Safe**: Concurrent writes with proper locking  

---

## 📈 Performance Metrics

**Example: Scraping 10 Places with 50 Reviews Each**

| Method | Time | Speed Gain |
|--------|------|-----------|
| Sequential (1 worker) | ~10 min | Baseline |
| Parallel (2 workers) | ~6 min | **1.67x faster** |
| Parallel (3 workers) | ~4.5 min | **2.2x faster** |

💡 Going from 1 worker → 2 workers gives the best speedup with minimal detection risk!

---

## 🛡️ Anti-Bot Features

When you run the scraper, it automatically:

1. **Rotates User Agents** - Appears as different browsers/OS
2. **Adds Human-Like Delays** - Variable delays between actions
3. **Hides WebDriver Signals** - Uses stealth JavaScript injection
4. **Disables Images** - Faster page loads, less bandwidth
5. **Randomizes Clicks** - Clicks feel natural, not automated
6. **Staggered Scrolling** - Scrolls in chunks with pauses

---

## ⚠️ If You Get Blocked

**Symptoms:**
- Scraper hangs / timeouts
- Returns 403 Forbidden
- IP shows up in CAPTCHA

**Solutions:**
1. Stop immediately
2. Reduce workers: `--workers 1`
3. Wait 1-2 hours
4. Try again with smaller batches
5. Consider using a VPN

---

## 📝 Output Format

Your `data/output.csv` will have columns:

- `id_review` - Unique review ID
- `caption` - Review text
- `rating` - Star rating (1-5)
- `username` - Who wrote it
- `relative_date` - When (e.g., "2 weeks ago")
- `retrieval_date` - When you scraped it
- Plus 4 more columns with user info

See `OPTIMIZATION_GUIDE.md` for full details.

---

## 🎯 Common Commands

```bash
# Basic: 50 reviews from URLs in urls.txt
python scraper.py

# Custom: 200 reviews, 2 workers, include source URLs
python scraper.py --N 200 --workers 2 --source

# Sorted by highest rating instead of newest
python scraper.py --sort_by highest_rating --workers 2

# Save to different file
python scraper.py --o my_reviews.csv --workers 2

# Debug mode (see browser)
python scraper.py --debug --workers 1 --N 10

# All options
python scraper.py --help
```

---

## 💰 Why This Scraper is Better

| Feature | Old | New |
|---------|-----|-----|
| **Speed** | Sequential | **2-4x Parallel** |
| **Bot Detection** | Basic delays | **Advanced stealth** |
| **User Agents** | None | **Rotation** |
| **Workers** | 1 | **Configurable** |
| **Progress** | None | **Real-time stats** |
| **Image Loading** | Yes | **Disabled** |
| **Headless** | Optional | **Default** |

---

## 🔧 Advanced Configuration

For power users, see `config.py`:

```python
from config import get_config

# Use predefined configs
safe_config = get_config('safe')      # 1 worker, max stealth
balanced_config = get_config('balanced')  # 2 workers, balanced
fast_config = get_config('fast')      # 3 workers, higher speed
```

---

## 📞 Troubleshooting

**Q: How many workers should I use?**  
A: Start with 2. Higher = more detection risk. Max recommended is 3.

**Q: Why does it pause between actions?**  
A: That's the anti-detection feature! It makes the scraper appear human.

**Q: Can I speed up the delays?**  
A: Edit `DELAY_RANGE_*` in `googlemaps.py`, but higher speed = higher detection risk.

**Q: Is it legal?**  
A: Check Google Maps ToS and local laws. Use responsibly for research/educational purposes.

**Q: How many reviews can I scrape?**  
A: Most places have 500-10,000+ reviews. Start with `--N 100` to test.

---

## 📚 Learn More

For detailed documentation:
- **`OPTIMIZATION_GUIDE.md`** - Full optimization details
- **`googlemaps.py`** - Core scraping logic (well-commented)
- **`parallel_scraper.py`** - Parallel processing implementation

---

## 🎓 Next Steps

1. ✅ Install requirements
2. ✅ Prepare URLs file  
3. ✅ Run first test: `python scraper.py --N 10 --workers 2`
4. ✅ Check output in `data/output.csv`
5. ✅ Scale up with more URLs/reviews
6. ✅ Monitor for blocks, adjust workers if needed

---

**Happy scraping!** 🎉
