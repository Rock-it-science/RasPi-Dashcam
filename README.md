The goal:
 - Record video in segments
 - When button is pressed, "lock-in" the current segment and the one before it
 - If button is not pressed, delete segment after the segment following it has finished recording

Hardware setup:
  1. Plug in raspicam
  2. Wiring diagram (TODO)
  3. Flash drive in USB slot

 Software Installation:
  1. Clone repo to raspi (on SD card)
  2. `chmod +x mountusb`
  3. `./mountusb`