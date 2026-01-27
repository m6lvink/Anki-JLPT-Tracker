# Anki JLPT Tracker

An Anki 2.1+ add-on that tracks your card progress against JLPT (Japanese Language Proficiency Test) vocabulary and grammar requirements.

## Features

* **Real-time Dashboard:** Automatically injects a progress dashboard into the Anki Deck Browser and Overview screens.
* **JLPT Levels:** Presets for N5 through N1 based on standard passing requirements.
* **Customizable Targets:** Select specific decks and Note Types (Vocabulary vs. Grammar) to track.
* **Study Estimation:** Calculates completion dates based on your daily "New Card" history.
* **Minimizable UI:** Toggle between a detailed dashboard and a subtle progress pill.

## Project Structure

This project has been refactored for modularity and ease of maintenance:

* `__init__.py`: Entry point. Handles Anki hooks (`will_render_content`) and direct HTML injection.
* `config_manager.py`: Handles loading/saving user settings and level presets.
* `db_utils.py`: Contains SQL queries and logic for counting card distributions.
* `view_manager.py`: Generates the HTML string for the dashboard.
* `gui.py`: PyQt6 definitions for the Settings dialog and color pickers.
* `web/`: Contains static assets (CSS, HTML templates).

## Installation

1.  Download the latest release or clone this repository.
2.  Copy the `Anki-JLPT-Tracker` folder into your Anki `addons21` directory.
3.  Restart Anki.

## Usage

1.  **Open Settings:** Go to `Tools > JLPT Tracker Settings` or click the Gear icon on the dashboard.
2.  **Configure Decks:** Select the specific decks you are using for Japanese study (supports multi-selection).
3.  **Map Note Types:** The add-on detects your Note Types. Assign them to "Vocab", "Grammar", or "Ignore".
4.  **Set Deadline:** (Optional) Enter your exam date to see a countdown.

## License

MIT License