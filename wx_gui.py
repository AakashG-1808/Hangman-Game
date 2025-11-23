# gui.py
import wx
from hangman_stages import HANGMAN_STAGES
from game_logic import random_word, GameState, HighScoreManagerCSV

HS_MANAGER = HighScoreManagerCSV()

def main():
    app = wx.App(False)
    frame = wx.Frame(None, title="Hangman Game", size=(920,640))
    panel = wx.Panel(frame)

    # Top bar 
    top_sizer = wx.BoxSizer(wx.HORIZONTAL)
    top_sizer.Add(wx.StaticText(panel, label="Difficulty:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)

    choice_diff = wx.Choice(panel, choices=["easy", "medium", "hard"])
    choice_diff.SetSelection(0)
    top_sizer.Add(choice_diff, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 12)

    btn_start = wx.Button(panel, label="Start Game")
    top_sizer.Add(btn_start, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)

    btn_high = wx.Button(panel, label="High Scores")
    top_sizer.Add(btn_high, 0, wx.ALIGN_CENTER_VERTICAL)

    top_sizer.AddStretchSpacer(1)

    # Game panel 
    game_panel = wx.Panel(panel)
    game_panel.SetMinSize((800, 480))

    main_vbox = wx.BoxSizer(wx.VERTICAL)
    main_vbox.Add(top_sizer, 0, wx.ALL | wx.EXPAND, 12)
    main_vbox.Add(game_panel, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
    panel.SetSizer(main_vbox)

    state = {}

    # Build Game UI
    
    def build_game_ui(difficulty, secret_word):
        game_panel.DestroyChildren()
        if game_panel.GetSizer():
            game_panel.GetSizer().Clear(True)

        vbox = wx.BoxSizer(wx.VERTICAL)
        gs = GameState(secret_word, lives=10)
        state["gs"] = gs
        state["difficulty"] = difficulty

        # ASCII + Word 
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        ascii_ctrl = wx.TextCtrl(
            game_panel, value=HANGMAN_STAGES[0],
            style=wx.TE_MULTILINE | wx.TE_READONLY, size=(260,260)
        )
        ascii_ctrl.SetFont(wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        hbox.Add(ascii_ctrl, 0, wx.RIGHT, 20)

        word_display = wx.StaticText(game_panel, label=" ".join(gs.display))
        word_display.SetFont(wx.Font(22, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        word_box = wx.BoxSizer(wx.VERTICAL)
        word_box.Add(wx.StaticText(game_panel, label="Word:"), 0, wx.BOTTOM, 6)
        word_box.Add(word_display, 0, wx.EXPAND)
        hbox.Add(word_box, 1, wx.EXPAND)

        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 6)

        # Status 
        guessed_val = wx.StaticText(game_panel, label="None")
        lives_val = wx.StaticText(game_panel, label=str(gs.lives))

        vbox.Add(wx.StaticText(game_panel, label="Guessed:"), 0, wx.LEFT | wx.TOP, 6)
        vbox.Add(guessed_val, 0, wx.LEFT, 12)
        vbox.Add(wx.StaticText(game_panel, label="Lives:"), 0, wx.LEFT | wx.TOP, 6)
        vbox.Add(lives_val, 0, wx.LEFT, 12)

        vbox.AddSpacer(12)

        # Input rows 
        entry_letter = wx.TextCtrl(game_panel, size=(80, -1), style=wx.TE_PROCESS_ENTER)
        btn_guess_letter = wx.Button(game_panel, label="Guess Letter")

        row1 = wx.BoxSizer(wx.HORIZONTAL)
        row1.Add(wx.StaticText(game_panel, label="Letter:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        row1.Add(entry_letter, 0, wx.RIGHT, 8)
        row1.Add(btn_guess_letter, 0)
        vbox.Add(row1, 0, wx.ALL, 6)

        entry_full = wx.TextCtrl(game_panel, size=(420, -1), style=wx.TE_PROCESS_ENTER)
        btn_guess_full = wx.Button(game_panel, label="Guess Full")

        row2 = wx.BoxSizer(wx.HORIZONTAL)
        row2.Add(wx.StaticText(game_panel, label="Full Guess:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        row2.Add(entry_full, 1, wx.RIGHT, 8)
        row2.Add(btn_guess_full, 0)
        vbox.Add(row2, 0, wx.ALL | wx.EXPAND, 6)

        # Lower buttons
        btn_restart = wx.Button(game_panel, label="Restart (Ctrl+R)")
        btn_quit = wx.Button(game_panel, label="Quit (ESC)")

        row3 = wx.BoxSizer(wx.HORIZONTAL)
        row3.Add(btn_restart, 0, wx.RIGHT, 10)
        row3.AddStretchSpacer(1)
        row3.Add(btn_quit, 0)
        vbox.Add(row3, 0, wx.ALL | wx.EXPAND, 6)

        game_panel.SetSizer(vbox)
        game_panel.Layout()

        state.update({
            "ascii_ctrl": ascii_ctrl,
            "word_display": word_display,
            "guessed_val": guessed_val,
            "lives_val": lives_val,
            "entry_letter": entry_letter,
            "entry_full": entry_full,
            "btn_guess_letter": btn_guess_letter,
            "btn_guess_full": btn_guess_full,
            "btn_restart": btn_restart,
            "btn_quit": btn_quit,
        })

        # UI update
        def update_ui():
            word_display.SetLabel(" ".join(gs.display))
            guessed_val.SetLabel(", ".join(sorted(gs.guessed)) if gs.guessed else "None")
            lives_val.SetLabel(str(gs.lives))
            wrong = gs.wrong_count()
            ascii_ctrl.SetValue(HANGMAN_STAGES[min(wrong, len(HANGMAN_STAGES)-1)])

        # Guess handlers
        def guess_letter(evt=None):
            letter = entry_letter.GetValue().strip().lower()
            entry_letter.SetValue("")
            if not letter:
                return
            status, _ = gs.guess_letter(letter)
            if status == "invalid":
                wx.MessageBox("Enter a single A-Z letter.", "Invalid")
            elif status == "already":
                wx.MessageBox(f"You already guessed {letter}, try another.", "Already Guessed")
            update_ui()
            if gs.is_won(): win()
            elif gs.is_lost(): lose()

        def guess_full(evt=None):
            attempt = entry_full.GetValue().strip().lower()
            entry_full.SetValue("")
            if not attempt:
                return
            result, _ = gs.guess_full(attempt)
            update_ui()
            if result is True: win()
            elif gs.is_lost(): lose()

        def win():
            dlg = wx.TextEntryDialog(frame, "You won! Enter your name:", "Victory!")
            name = "Anonymous"
            if dlg.ShowModal() == wx.ID_OK:
                name = dlg.GetValue().strip() or "Anonymous"
            dlg.Destroy()
            HS_MANAGER.add_score(name, difficulty, gs.secret, gs.lives, len(gs.guessed))
            wx.MessageBox("Score saved!", "Win")

        def lose():
            ascii_ctrl.SetValue(HANGMAN_STAGES[-1])
            wx.MessageBox(f"You lost! Word was: {gs.secret}", "Game Over")

        # Restart / Quit
        def restart(evt=None):
            new_word = gs.restart(difficulty)
            build_game_ui(difficulty, new_word)

        def quit_game(evt=None):
            frame.Close()

        # Bind inputs + buttons + Enter events
        btn_guess_letter.Bind(wx.EVT_BUTTON, guess_letter)
        btn_guess_full.Bind(wx.EVT_BUTTON, guess_full)
        entry_letter.Bind(wx.EVT_TEXT_ENTER, guess_letter)
        entry_full.Bind(wx.EVT_TEXT_ENTER, guess_full)
        btn_restart.Bind(wx.EVT_BUTTON, restart)
        btn_quit.Bind(wx.EVT_BUTTON, quit_game)

        # GLOBAL KEYBOARD HOOK (Ctrl+R, ESC)
        def on_key(event):
            key = event.GetKeyCode()

            # Ctrl + R → Restart
            if key == ord('R') and event.ControlDown():
                restart()
                return

            # ESC → Quit
            if key == wx.WXK_ESCAPE:
                quit_game()
                return

            event.Skip()

        frame.Bind(wx.EVT_CHAR_HOOK, on_key)

        entry_letter.SetFocus()
        update_ui()

    def on_start(evt):
        diff = choice_diff.GetStringSelection() or "easy"
        secret = random_word(diff)
        build_game_ui(diff, secret)

    def on_show_high(evt):
        top = HS_MANAGER.get_top(10)
        if not top:
            wx.MessageBox("No scores yet!", "High Scores")
            return
        msg = "\n".join(
            f"{i+1}. {e['name']} - {e['difficulty']} - lives: {e['lives']} - word: {e['secret']}"
            for i, e in enumerate(top)
        )
        wx.MessageBox(msg, "High Scores")

    btn_start.Bind(wx.EVT_BUTTON, on_start)
    btn_high.Bind(wx.EVT_BUTTON, on_show_high)

    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
