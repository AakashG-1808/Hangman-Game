import random
import os
import csv
from datetime import datetime
from wordfreq import top_n_list

HIGHSCORE_CSV = "highscores.csv"

def random_word(difficulty):
    words = top_n_list("en", 10000)
    words = [w for w in words if w.isalpha()]

    if difficulty == "easy":
        pool = [w for w in words if 3 <= len(w) <= 6]
    elif difficulty == "medium":
        pool = [w for w in words if 7 <= len(w) <= 10]
    elif difficulty == "hard":
        pool = [w for w in words if len(w) >= 11]
    else:
        print("Invalid difficulty")
        pool = words

    return random.choice(pool or words)


def make_display(secret):
    return [" " if ch == " " else "_" for ch in secret]

class GameState:
    def __init__(self, secret, lives=10):
        self.secret = secret.lower()
        self.display = make_display(self.secret)
        self.guessed = set()
        self.lives = lives
        self.lives_max = lives

    def wrong_count(self):
        return self.lives_max - self.lives

    def is_won(self):
        return "_" not in self.display

    def is_lost(self):
        return self.lives <= 0

    def guess_letter(self, letter):
        if not letter or len(letter) != 1 or not letter.isalpha():
            return ("invalid", "Enter a single letter.")

        g = letter.lower()

        if g in self.guessed:
            return ("already", f"You already guessed '{g}'")

        self.guessed.add(g)

        if g in self.secret:
            for i, ch in enumerate(self.secret):
                if ch == g:
                    self.display[i] = g
            return ("ok", f"Correct guess: {g}")
        else:
            self.lives -= 1
            return ("miss", f"Wrong guess: {g}")

    def guess_full(self, attempt):
        attempt = (attempt or "").lower().strip()

        if attempt == self.secret:
            self.display = list(self.secret)
            return (True, "Correct full guess.")
        else:
            self.lives -= 1
            return (False, "Incorrect full guess.")

    def restart(self, difficulty):
        new_secret = random_word(difficulty)
        self.__init__(new_secret, lives=self.lives_max)
        return new_secret


# CSV-BASED HIGH SCORE MANAGER
class HighScoreManagerCSV:
    def __init__(self, filename=HIGHSCORE_CSV):
        self.filename = filename

        if not os.path.exists(filename):
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["name", "difficulty", "secret", "lives", "guesses", "date"])

    def add_score(self, name, difficulty, secret, lives, guesses):
        with open(self.filename, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                name or "Anonymous",
                difficulty,
                secret,
                lives,
                guesses,
                datetime.now().isoformat() + "Z"
            ])

    def get_top(self, limit=10):
        with open(self.filename, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Sort by lives (desc), then date (asc)
        rows.sort(key=lambda r: (-int(r["lives"]), r["date"]))
        return rows[:limit]

    def clear(self):
        with open(self.filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "difficulty", "secret", "lives", "guesses", "date"])
