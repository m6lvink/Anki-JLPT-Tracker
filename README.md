# Anki JLPT Tracker

An Anki 2.1+ add-on that tracks your card progress against JLPT (Japanese Language Proficiency Test) vocabulary and grammar requirements.

## Features

* **Real-time Dashboard:** Automatically injects a progress dashboard into the Anki Deck Browser and Overview screens.
* **JLPT Levels:** Presets for N5 through N1 based on standard passing requirements.
* **Customizable Targets:** Select specific decks and Note Types (Vocabulary vs. Grammar) to track.
* **Study Estimation:** Calculates completion dates based on your daily study history.
* **Minimizable UI:** Toggle between a detailed dashboard and a subtle progress pill.
* **Background Opacity:** Adjust the panel transparency so underlying Anki themes remain visible.
* **Tracking Mode:** Choose to track Vocab only, Grammar only, or both together.

## Project Structure

* `__init__.py`: Entry point. Handles Anki hooks and HTML injection.
* `config_manager.py`: Handles loading/saving user settings and level presets.
* `db_utils.py`: SQL queries and logic for counting card distributions.
* `view_manager.py`: Generates the HTML string for the dashboard.
* `gui.py`: PyQt6 definitions for the Settings dialog and color pickers.
* `progress_utils.py`: Daily snapshot tracking and completion estimation.
* `web/`: Static assets (CSS, HTML templates).

## Installation

1. Download the latest release or clone this repository.
2. Copy the `Anki-JLPT-Tracker` folder into your Anki `addons21` directory.
3. Restart Anki.

## Usage

1. **Open Settings:** Go to `Tools > JLPT Tracker Settings` or click the gear icon on the dashboard.
2. **Configure Decks:** Select the decks you are using for Japanese study (supports multi-deck selection).
3. **Map Note Types:** Assign each Note Type to "Vocab", "Grammar", or "Ignore".
4. **Set Deadline:** (Optional) Enter your exam date to see a countdown instead of an estimate.
5. **Opacity:** Drag the Background Opacity slider if you want the panel to be semi-transparent.
6. **Tracking Mode:** Select whether to track Vocab only, Grammar only, or both.

## Versions

**v3.0.0**
- Background opacity control (panel transparency, text stays fully visible)
- Tracking mode selection: Vocab only, Grammar only, or both
- Progress estimate and growth rate now respect the selected tracking mode

**v2.x**
- Multi-deck selection support
- Legacy single-deck config migration

**v1.x**
- Initial release

## License

MIT License
