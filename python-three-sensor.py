#!/usr/bin/env python3
"""
Simple Arduino Sensor Reader with Delta Threshold Triggers
Basic script to quickly read and display Arduino sensor data
- Photoresistor triggers cmd+shift+alt+s when increase > threshold
- Sound sensor triggers cmd+shift+alt+m when increase > threshold
"""

import serial
import time
import glob
import re
from pynput.keyboard import Key, Controller

def find_arduino_port():
    """Find Arduino port automatically"""
    patterns = ['/dev/cu.usbmodem*', '/dev/cu.usbserial*', '/dev/cu.wchusb*']
    ports = []
    for pattern in patterns:
        ports.extend(glob.glob(pattern))
    return ports[0] if ports else None

def trigger_stress_action():
    """Trigger stress action: cmd+shift+alt+s"""
    keyboard = Controller()
    
    # Press all modifier keys
    keyboard.press(Key.cmd)
    keyboard.press(Key.shift)
    keyboard.press(Key.alt)
    keyboard.press('x')
    
    # Release all keys in reverse order
    keyboard.release('x')
    keyboard.release(Key.alt)
    keyboard.release(Key.shift)
    keyboard.release(Key.cmd)
    
    print(f"🪿 Goose Take The Wheel (❤️‍🔥 Heartrate Spike)")

def trigger_sound_action():
    """Trigger sound action: cmd+shift+alt+m"""
    keyboard = Controller()
    
    # Press all modifier keys
    keyboard.press(Key.cmd)
    keyboard.press(Key.shift)
    keyboard.press(Key.alt)
    keyboard.press('x')
    
    # Release all keys in reverse order
    keyboard.release('x')
    keyboard.release(Key.alt)
    keyboard.release(Key.shift)
    keyboard.release(Key.cmd)
    
    print(f"🪿 Goose Take The Wheel (🔊 Sound Spike)")

def extract_sensor_values(line):
    """Extract both sensor values from Arduino output"""
    photoresistor_value = None
    sound_value = None
    
    # Look for "Photoresistor: XXX" pattern
    photo_match = re.search(r'Photoresistor:\s*(\d+\.?\d*)', line)
    if photo_match:
        try:
            photoresistor_value = float(photo_match.group(1))
        except ValueError:
            pass
    
    # Look for "Sound Sensor: XXX" pattern
    sound_match = re.search(r'Sound Sensor:\s*(\d+\.?\d*)', line)
    if sound_match:
        try:
            sound_value = float(sound_match.group(1))
        except ValueError:
            pass
    
    return photoresistor_value, sound_value

def calculate_baseline(values, window_size=10):
    """Calculate rolling average baseline"""
    if len(values) < window_size:
        return sum(values) / len(values) if values else 0
    return sum(values[-window_size:]) / window_size

def read_arduino_data(port=None, duration=100, photo_threshold=100, sound_threshold=50):
    """Read Arduino data for specified duration with delta threshold triggers"""
    
    # Find port if not specified
    if not port:
        port = find_arduino_port()
        if not port:
            print("No Arduino found. Please specify port manually.")
            return
    
    print(f"Connecting to Arduino on {port}...")
    print(f"🚨 Photoresistor increase threshold: +{photo_threshold}")
    print(f"🔊 Sound sensor increase threshold: +{sound_threshold}")
    print("📊 Collecting baseline data for first 10 readings...")
    
    try:
        # Connect to Arduino
        arduino = serial.Serial(port, 9600, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset
        
        print(f"Reading data for {duration} seconds... (Press Ctrl+C to stop)")
        
        start_time = time.time()
        last_stress_trigger = 0  # Prevent rapid repeated stress triggers
        last_sound_trigger = 0   # Prevent rapid repeated sound triggers
        
        # Track sensor history for baseline calculation
        photo_history = []
        sound_history = []
        
        while time.time() - start_time < duration:
            if arduino.in_waiting > 0:
                line = arduino.readline().decode('utf-8').strip()
                print(line)
                
                # Extract both sensor values
                photo_value, sound_value = extract_sensor_values(line)
                current_time = time.time()
                
                # Process photoresistor data
                if photo_value is not None:
                    photo_history.append(photo_value)
                    
                    if len(photo_history) > 3:  # Need some history before triggering
                        photo_baseline = calculate_baseline(photo_history)
                        photo_increase = photo_value - photo_baseline
                        
                        print(f"📸 Photo: {photo_value:.1f} (baseline: {photo_baseline:.1f}, Δ: {photo_increase:+.1f})")
                        
                        if photo_increase > photo_threshold and (current_time - last_stress_trigger) > 2.0:
                            print(f"❤️‍🔥 YELLIN : +{photo_increase:.1f} > +{photo_threshold}")
                            trigger_stress_action()
                            last_stress_trigger = current_time
                
                # Process sound sensor data
                if sound_value is not None:
                    sound_history.append(sound_value)
                    
                    if len(sound_history) > 3:  # Need some history before triggering
                        sound_baseline = calculate_baseline(sound_history)
                        sound_increase = sound_value - sound_baseline
                        
                        print(f"🔊 Sound: {sound_value:.1f} (baseline: {sound_baseline:.1f}, Δ: {sound_increase:+.1f})")
                        
                        if sound_increase > sound_threshold and (current_time - last_sound_trigger) > 2.0:
                            print(f"🔊 SOUND SPIKE: +{sound_increase:.1f} > +{sound_threshold}")
                            trigger_sound_action()
                            last_sound_trigger = current_time
                        
            time.sleep(0.01)
                
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'arduino' in locals():
            arduino.close()
            print("Disconnected from Arduino")

if __name__ == "__main__":
    # Read data with delta thresholds for increases
    read_arduino_data(photo_threshold=15, sound_threshold=2)