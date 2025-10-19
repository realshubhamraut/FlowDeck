# Birthday Wishes & Daily Quotes Feature

## ✨ Overview
Added two new engaging features to enhance the FlowDeck dashboard experience:
1. **Date of Birth tracking** for team members
2. **Daily Motivational Quotes** from free API
3. **Birthday Celebrations** with personalized wishes

## 🎂 Features Implemented

### 1. Date of Birth Field
- ✅ Added `date_of_birth` column to User model (Date type)
- ✅ Database migration script (`add_date_of_birth.py`)
- ✅ Helper methods in User model:
  - `is_birthday_today()` - Check if today is user's birthday
  - `age()` - Calculate current age
- ✅ Updated create user form with birthday input field
- ✅ Updated edit user form with birthday input field
- ✅ Birthday cake icon for visual appeal
- ✅ Date validation (max date is today)

### 2. Daily Motivational Quotes
- ✅ Created `app/utils/quotes.py` utility module
- ✅ Integration with **ZenQuotes API** (free, no auth required)
- ✅ 20 fallback quotes for offline/API failure scenarios
- ✅ Beautiful gradient card display on dashboard
- ✅ Caching to avoid excessive API calls

### 3. Birthday Celebrations Dashboard
- ✅ Automatic detection of today's birthdays
- ✅ Beautiful pink gradient alert card
- ✅ Displays all team members celebrating birthdays
- ✅ Shows profile pictures or avatar initials
- ✅ Personalized birthday messages
- ✅ Age badge display
- ✅ Designation information
- ✅ Dismissible alert

## 📁 Files Changed

### Models
- **app/models/user.py**
  - Added `date_of_birth` field (Date)
  - Added `is_birthday_today()` method
  - Added `age()` method

### Routes
- **app/routes/admin.py**
  - Updated `create_user()` to handle date_of_birth
  - Updated `edit_user()` to handle date_of_birth
  - Added `today` variable to template context

- **app/routes/dashboard.py**
  - Added imports for User, extract, and quotes utility
  - Query birthdays from organization users
  - Generate birthday wishes with personalized messages
  - Fetch daily motivational quote
  - Pass data to dashboard template

### Templates
- **app/templates/admin/create_user.html**
  - Added date_of_birth input field with birthday cake icon
  - Added helpful text about celebrations

- **app/templates/admin/edit_user.html**
  - Added date_of_birth input field (pre-filled with existing value)
  - Date formatting for display

- **app/templates/dashboard/index.html**
  - Added Daily Quote card (gradient purple design)
  - Added Birthday Wishes alert (gradient pink design)
  - Profile pictures and avatars for birthday users
  - Age badges
  - Dismissible alert functionality

### Utilities
- **app/utils/quotes.py** (NEW)
  - `get_quote_from_api()` - Fetch from ZenQuotes API
  - `get_daily_quote()` - Get quote with fallback
  - `get_birthday_message()` - Generate personalized birthday messages
  - 20 hardcoded fallback quotes

### Database
- **add_date_of_birth.py** (NEW)
  - Migration script to add date_of_birth column
  - Safe execution (checks if column exists)

## 🎨 Design Features

### Daily Quote Card
```
- Gradient background: #667eea → #764ba2 (purple)
- Large quote icon (opacity 0.3)
- Italic font style for quote text
- Author attribution aligned right
- White text on gradient
- Rounded corners (20px)
- Shadow effect
```

### Birthday Wishes Alert
```
- Gradient background: #f093fb → #f5576c (pink)
- Birthday cake icon in heading
- Emoji decorations (🎉)
- Profile pictures with white border and shadow
- Glass morphism effect on user cards
- Age badges (white background, pink text)
- Dismissible with close button
- Call-to-action message
```

## 🔌 API Integration

### ZenQuotes API
- **Endpoint**: `https://zenquotes.io/api/random`
- **Method**: GET
- **Auth**: None required
- **Timeout**: 3 seconds
- **Caching**: Yes (lru_cache)
- **Fallback**: 20 local quotes

**Response Format**:
```json
[{
  "q": "Quote text",
  "a": "Author name"
}]
```

## 📊 Database Schema Change

```sql
ALTER TABLE users ADD COLUMN date_of_birth DATE;
```

**Migration Status**: ✅ Completed successfully

## 🚀 Usage

### For Admins:
1. Go to **Admin → Users → Create User** or **Edit User**
2. Fill in the "Date of Birth" field
3. Save the user

### For All Users:
1. Open dashboard
2. See **daily motivational quote** at the top
3. See **birthday wishes** for team members celebrating today
4. Birthday cards show:
   - User's name and photo
   - Personalized message
   - Age (if available)
   - Designation
   - Option to send message

## 🎯 Benefits

1. **Team Engagement**: Celebrate birthdays together
2. **Daily Motivation**: Start each day with inspiring quotes
3. **Personal Touch**: Age tracking and personalized messages
4. **Visual Appeal**: Beautiful gradient designs
5. **User-Friendly**: Easy to add/edit birthdays
6. **Reliable**: Works offline with fallback quotes
7. **Performance**: Cached API calls

## 🛠️ Technical Details

### Dependencies
- **requests** library (for API calls)
- **SQLAlchemy** extract function (for birthday queries)

### Performance
- API calls are cached with `lru_cache`
- Birthday query optimized with month/day extraction
- Fallback system ensures no downtime

### Error Handling
- Try-except blocks for API calls
- Timeout protection (3 seconds)
- Graceful fallback to local quotes
- None checks for missing birthdays

## 🎉 Example Birthday Messages

- "🎉 Happy Birthday Alice! Wishing you a fantastic day filled with joy and success!"
- "🎂 Happy Birthday Bob! May this year bring you closer to your dreams!"
- "🎈 Cheers to Charlie! Hope your special day is as amazing as you are!"
- "🎊 Happy Birthday Diana! May your day be filled with laughter and happiness!"
- "🌟 Wishing Eve a wonderful birthday! Here's to another year of great achievements!"

## 📝 Future Enhancements (Optional)

- [ ] Email notifications for birthdays
- [ ] Birthday calendar view
- [ ] Upcoming birthdays widget (next 7 days)
- [] Birthday gift suggestions
- [ ] Team birthday statistics
- [ ] Custom birthday messages
- [ ] Birthday greeting cards
- [ ] Integration with chat for birthday wishes
- [ ] Slack/Teams birthday notifications

## ✅ Testing Checklist

- [x] Database migration runs successfully
- [x] Create user with birthday works
- [x] Edit user birthday works
- [x] Dashboard shows quotes
- [x] Birthday detection works correctly
- [x] API fallback works when offline
- [x] Age calculation is accurate
- [x] Profile pictures display correctly
- [x] Avatars show for users without photos
- [x] Dismiss button works on birthday alert

## 🎊 Conclusion

The Birthday Wishes and Daily Quotes feature adds a personal and motivational touch to FlowDeck, making the workspace more engaging and team-oriented. Users start their day with inspiration and celebrate special moments together!

---

**Created**: October 19, 2025
**Status**: ✅ Fully Implemented and Tested
**Migration**: ✅ Database Updated Successfully
