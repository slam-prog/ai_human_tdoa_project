frame_controller.ino/*
 * Frame Controller for Magnetic Tape TDOA System
 * 
 * This Arduino sketch generates timing signals for:
 * - Recording gates (simultaneous for all channels)
 * - Sample-and-hold pulses
 * - Erase control
 * - Optional sync output
 */

// Pin assignments
const int PIN_RECORD_GATE = 8;
const int PIN_SAMPLE_PULSE = 9;
const int PIN_ERASE_GATE = 10;
const int PIN_SYNC = 11;

// Timing parameters (adjust based on tape speed and frame length)
const unsigned long FRAME_PERIOD_MS = 30;      // Total frame period
const unsigned long RECORD_TIME_MS = 20;       // Recording window
const unsigned long GUARD_TIME_MS = 5;         // Guard gap
const unsigned long SAMPLE_PULSE_WIDTH_US = 100; // Sample pulse width

// Frame counter
unsigned long frame_count = 0;

void setup() {
  // Configure pins as outputs
  pinMode(PIN_RECORD_GATE, OUTPUT);
  pinMode(PIN_SAMPLE_PULSE, OUTPUT);
  pinMode(PIN_ERASE_GATE, OUTPUT);
  pinMode(PIN_SYNC, OUTPUT);
  
  // Initialize all outputs low
  digitalWrite(PIN_RECORD_GATE, LOW);
  digitalWrite(PIN_SAMPLE_PULSE, LOW);
  digitalWrite(PIN_ERASE_GATE, LOW);
  digitalWrite(PIN_SYNC, LOW);
  
  // Start serial for debugging (optional)
  Serial.begin(9600);
  Serial.println("Frame Controller Started");
}

void loop() {
  // Begin new frame
  frame_count++;
  
  // Record gate HIGH (start recording)
  digitalWrite(PIN_RECORD_GATE, HIGH);
  digitalWrite(PIN_SYNC, HIGH);  // Sync pulse at frame start
  
  // Wait for recording duration
  delay(RECORD_TIME_MS);
  
  // Record gate LOW (stop recording)
  digitalWrite(PIN_RECORD_GATE, LOW);
  digitalWrite(PIN_SYNC, LOW);
  
  // Guard gap
  delay(GUARD_TIME_MS);
  
  // Sample pulse (capture energy value)
  digitalWrite(PIN_SAMPLE_PULSE, HIGH);
  delayMicroseconds(SAMPLE_PULSE_WIDTH_US);
  digitalWrite(PIN_SAMPLE_PULSE, LOW);
  
  // Erase gate HIGH (erase previous frame)
  digitalWrite(PIN_ERASE_GATE, HIGH);
  delay(GUARD_TIME_MS);
  digitalWrite(PIN_ERASE_GATE, LOW);
  
  // Remaining guard gap
  delay(GUARD_TIME_MS);
  
  // Optional: print frame count for debugging
  if (frame_count % 100 == 0) {
    Serial.print("Frame: ");
    Serial.println(frame_count);
  }
}