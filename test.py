from pupil_labs.realtime_api.simple import discover_one_device, discover_devices
from pupil_labs.realtime_api.simple import Device

print("Looking for a device")
# device1 = Device("pi.local", 8080)
devicesFound = discover_devices(10) # a list of all devices found
device1 = Device("192.168.1.129", 8080)
if device1 is None:
    print("No device found.")
    raise SystemExit(-1)
print(f"Connecting to {device1}...")     

print(device1.phone_ip)
print(device1.phone_name)
print(device1.phone_id)
print(device1.battery_level_percent)
