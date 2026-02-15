from datetime import date, timedelta, time
from app.db.session import SessionLocal
from app.db import models

def seed_blocked_slots():
    db = SessionLocal()
    start_date = date.today()
    
    
    schedule = {
        0: (12, 13), # Mon
        1: (12, 13), # Tue
        2: (13, 14), # Wed
        3: (14, 15), # Thu
        4: (12, 13)  # Fri
    }

    try:
        for i in range(30):
            current_date = start_date + timedelta(days=i)
            day_num = current_date.weekday()

            # Only block weekdays (Mon-Fri)
            if day_num in schedule:
                start_h, end_h = schedule[day_num]
                
                # Create the block object
                new_block = models.BlockedSlot(
                    date=current_date,
                    start_time=time(hour=start_h, minute=0),
                    end_time=time(hour=end_h, minute=0),
                    reason="Staff Break"
                )
                
                # Check if it already exists to avoid duplicates
                exists = db.query(models.BlockedSlot).filter(
                    models.BlockedSlot.date == current_date,
                    models.BlockedSlot.start_time == time(hour=start_h, minute=0)
                ).first()

                if not exists:
                    db.add(new_block)
        
        db.commit()
        print("Successfully seeded breaks for the next 30 days.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_blocked_slots()