from datetime import datetime, timezone
import RGB1602 as RGB1602

lcd = RGB1602.RGB1602(16, 2)
lcd.clear()

print(f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} LCD display cleared")
