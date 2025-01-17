# Communication

/dev/ttyUSB0
115200 baud, no parity

***

# Key

Data comes in every second

Empty line between packets

Each packet may contain other lines than these
Each line may contain more stuff at the end
All format strings are given between < and >, which do not appear in any other context

***

# Format strings

Fx(a,b) means a floating point number with x digits, of which between a and b are after the decimal point
Sx means a string with x characters

***

# ELECTRICITY READINGS

Timestamp
0-0:1.0.0(<YYMMDDhhmmss>

Lifetime power usage Tarrif 1 (in kWh)
1-0:1.8.1(<F9(3,3)>

Lifetime power usage Tarrif 2 (in kWh)
1-0:1.8.2(<F9(3,3)>

Current tarrif type (can be 0001 for Tarrif 1 or 0002 for Tarrif 2)
0-0:96.14.0(<S4>

Current power usage (in kWh)
1-0:1.7.0(<F5(3,3)>

***

# GAS READINGS

Timestamp and lifetime gas usage (in m3)
0-1:24.2.1(<YYMMDDhhmmss>W)(<F8(3,3)>
