# BronchoVision

## Changelog

---

### 2021-03 (Phantom version)

- **New Features**
        - Working Camera (Webcam/Bronchoscope/...) view
        - New Layout (2x1x3)
        - Moving Light added to the Virtual Camera (Brighter View)
- **Fixes**
        - Handled unwanted change in window size after loading patient
        - Fixed Crash in New Patient
---

### 2020-12 (Phantom version)

- **New Features**
        - Visualize Image/Tracker points before registration
        - Show the final Registration Matrix (Scale*Rotation, Translation)
- **Fixes**
        - Fixed tracker connection crash
        - Remove the cross mark, after resetting Virtual mode
        - Show correct and registered points, loaded in tracker offline section
        - Fixed errors in New/Load/Delete Patients

---

### 2020-11 (Phantom version)

- **New Features**
        - Adjusted orientation widget (man model) to match the orientation of the Phantom
        - Adjusted 2D views for the phantom
        - Extract/Load Image Centerline
        - Record/Load Tracker Centerline
        - Integrated Registration Process
        - Complete and working registration process
        - Added tracker status splash messages
        - Save Image Centerline, Tracker Centerline and Registration Matrix for the current patient and load them automatically on the next run
- **Fixes**
        - Fixed 2D view problem
        - Fixed tracker's crash
