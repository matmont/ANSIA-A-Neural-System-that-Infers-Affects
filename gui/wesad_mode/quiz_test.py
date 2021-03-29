import html
import json
import random
import tkinter as tk
from tkinter import IntVar, StringVar, DoubleVar
from tkinter import ttk

WIDTH = 700
HEIGHT = 600

DURATION = 1000 # seconds

# https://opentdb.com/api.php?amount=200&category=18&type=multiple
response = '{"response_code":0,"results":[{"category":"Science: Computers","type":"multiple","difficulty":"hard",' \
           '"question":"The Harvard architecture for micro-controllers added which additional bus?",' \
           '"correct_answer":"Instruction","incorrect_answers":["Address","Data","Control"]},{"category":"Science: ' \
           'Computers","type":"multiple","difficulty":"easy","question":"Which company was established on April 1st, ' \
           '1976 by Steve Jobs, Steve Wozniak and Ronald Wayne?","correct_answer":"Apple","incorrect_answers":[' \
           '"Microsoft","Atari","Commodore"]},{"category":"Science: Computers","type":"multiple",' \
           '"difficulty":"medium","question":"Which internet company began life as an online bookstore called ' \
           '&#039;Cadabra&#039;?","correct_answer":"Amazon","incorrect_answers":["eBay","Overstock","Shopify"]},' \
           '{"category":"Science: Computers","type":"multiple","difficulty":"easy","question":"What does the ' \
           '&quot;MP&quot; stand for in MP3?","correct_answer":"Moving Picture","incorrect_answers":["Music Player",' \
           '"Multi Pass","Micro Point"]},{"category":"Science: Computers","type":"multiple","difficulty":"easy",' \
           '"question":"When Gmail first launched, how much storage did it provide for your email?",' \
           '"correct_answer":"1GB","incorrect_answers":["512MB","5GB","Unlimited"]},{"category":"Science: Computers",' \
           '"type":"multiple","difficulty":"medium","question":"Moore&#039;s law originally stated that the number of ' \
           'transistors on a microprocessor chip would double every...","correct_answer":"Year","incorrect_answers":[' \
           '"Four Years","Two Years","Eight Years"]},{"category":"Science: Computers","type":"multiple",' \
           '"difficulty":"easy","question":"What does GHz stand for?","correct_answer":"Gigahertz",' \
           '"incorrect_answers":["Gigahotz","Gigahetz","Gigahatz"]},{"category":"Science: Computers",' \
           '"type":"multiple","difficulty":"medium","question":"What does AD stand for in relation to Windows ' \
           'Operating Systems? ","correct_answer":"Active Directory","incorrect_answers":["Alternative Drive",' \
           '"Automated Database","Active Department"]},{"category":"Science: Computers","type":"multiple",' \
           '"difficulty":"easy","question":"The programming language &#039;Swift&#039; was created to replace what ' \
           'other programming language?","correct_answer":"Objective-C","incorrect_answers":["C#","Ruby","C++"]},' \
           '{"category":"Science: Computers","type":"multiple","difficulty":"easy","question":"HTML is what type of ' \
           'language?","correct_answer":"Markup Language","incorrect_answers":["Macro Language","Programming ' \
           'Language","Scripting Language"]},{"category":"Science: Computers","type":"multiple","difficulty":"easy",' \
           '"question":"What amount of bits commonly equals one byte?","correct_answer":"8","incorrect_answers":["1",' \
           '"2","64"]},{"category":"Science: Computers","type":"multiple","difficulty":"hard","question":"How many Hz ' \
           'does the video standard PAL support?","correct_answer":"50","incorrect_answers":["59","60","25"]},' \
           '{"category":"Science: Computers","type":"multiple","difficulty":"easy","question":"Which computer ' \
           'hardware device provides an interface for all other connected devices to communicate?",' \
           '"correct_answer":"Motherboard","incorrect_answers":["Central Processing Unit","Hard Disk Drive",' \
           '"Random Access Memory"]},{"category":"Science: Computers","type":"multiple","difficulty":"medium",' \
           '"question":"On which computer hardware device is the BIOS chip located?","correct_answer":"Motherboard",' \
           '"incorrect_answers":["Hard Disk Drive","Central Processing Unit","Graphics Processing Unit"]},' \
           '{"category":"Science: Computers","type":"multiple","difficulty":"easy","question":"In the programming ' \
           'language Java, which of these keywords would you put on a variable to make sure it doesn&#039;t get ' \
           'modified?","correct_answer":"Final","incorrect_answers":["Static","Private","Public"]},' \
           '{"category":"Science: Computers","type":"multiple","difficulty":"easy","question":"What does the Prt Sc ' \
           'button do?","correct_answer":"Captures what&#039;s on the screen and copies it to your clipboard",' \
           '"incorrect_answers":["Nothing","Saves a .png file of what&#039;s on the screen in your screenshots folder ' \
           'in photos","Closes all windows"]},{"category":"Science: Computers","type":"multiple","difficulty":"easy",' \
           '"question":"What is the most preferred image format used for logos in the Wikimedia database?",' \
           '"correct_answer":".svg","incorrect_answers":[".png",".jpeg",".gif"]},{"category":"Science: Computers",' \
           '"type":"multiple","difficulty":"medium","question":"What did the name of the Tor Anonymity Network ' \
           'orignially stand for?","correct_answer":"The Onion Router","incorrect_answers":["The Only Router",' \
           '"The Orange Router","The Ominous Router"]},{"category":"Science: Computers","type":"multiple",' \
           '"difficulty":"medium","question":"What was the first commerically available computer processor?",' \
           '"correct_answer":"Intel 4004","incorrect_answers":["Intel 486SX","TMS 1000","AMD AM386"]},' \
           '{"category":"Science: Computers","type":"multiple","difficulty":"medium","question":"Which of these is ' \
           'the name for the failed key escrow device introduced by the National Security Agency in 1993?",' \
           '"correct_answer":"Clipper Chip","incorrect_answers":["Enigma Machine","Skipjack","Nautilus"]},' \
           '{"category":"Science: Computers","type":"multiple","difficulty":"hard","question":"The internet domain ' \
           '.fm is the country-code top-level domain for which Pacific Ocean island nation?",' \
           '"correct_answer":"Micronesia","incorrect_answers":["Fiji","Tuvalu","Marshall Islands"]},' \
           '{"category":"Science: Computers","type":"multiple","difficulty":"medium","question":"While Apple was ' \
           'formed in California, in which western state was Microsoft founded?","correct_answer":"New Mexico",' \
           '"incorrect_answers":["Washington","Colorado","Arizona"]},{"category":"Science: Computers",' \
           '"type":"multiple","difficulty":"medium","question":"How many cores does the Intel i7-6950X have?",' \
           '"correct_answer":"10","incorrect_answers":["12","8","4"]},{"category":"Science: Computers",' \
           '"type":"multiple","difficulty":"medium","question":"Which one of these is not an official development ' \
           'name for a Ubuntu release?","correct_answer":"Mystic Mansion","incorrect_answers":["Trusty Tahr",' \
           '"Utopic Unicorn","Wily Werewolf"]},{"category":"Science: Computers","type":"multiple",' \
           '"difficulty":"medium","question":"In the server hosting industry IaaS stands for...",' \
           '"correct_answer":"Infrastructure as a Service","incorrect_answers":["Internet as a Service","Internet and ' \
           'a Server","Infrastructure as a Server"]},{"category":"Science: Computers","type":"multiple",' \
           '"difficulty":"medium","question":"In CSS, which of these values CANNOT be used with the ' \
           '&quot;position&quot; property?","correct_answer":"center","incorrect_answers":["static","absolute",' \
           '"relative"]},{"category":"Science: Computers","type":"multiple","difficulty":"medium","question":"What is ' \
           'the correct term for the metal object in between the CPU and the CPU fan within a computer system?",' \
           '"correct_answer":"Heat Sink","incorrect_answers":["CPU Vent","Temperature Decipator","Heat Vent"]},' \
           '{"category":"Science: Computers","type":"multiple","difficulty":"medium","question":"In computing terms, ' \
           'typically what does CLI stand for?","correct_answer":"Command Line Interface","incorrect_answers":[' \
           '"Common Language Input","Control Line Interface","Common Language Interface"]},{"category":"Science: ' \
           'Computers","type":"multiple","difficulty":"medium","question":"How fast is USB 3.1 Gen 2 theoretically?",' \
           '"correct_answer":"10 Gb\/s","incorrect_answers":["5 Gb\/s","8 Gb\/s","1 Gb\/s"]},{"category":"Science: ' \
           'Computers","type":"multiple","difficulty":"medium","question":"Which operating system was released ' \
           'first?","correct_answer":"Mac OS","incorrect_answers":["Windows","Linux","OS\/2"]},{"category":"Science: ' \
           'Computers","type":"multiple","difficulty":"medium","question":".rs is the top-level domain for what ' \
           'country?","correct_answer":"Serbia","incorrect_answers":["Romania","Russia","Rwanda"]},' \
           '{"category":"Science: Computers","type":"multiple","difficulty":"hard","question":"Which data structure ' \
           'does FILO apply to?","correct_answer":"Stack","incorrect_answers":["Queue","Heap","Tree"]},' \
           '{"category":"Science: Computers","type":"multiple","difficulty":"hard","question":"Which of these is not ' \
           'a key value of Agile software development?","correct_answer":"Comprehensive documentation",' \
           '"incorrect_answers":["Individuals and interactions","Customer collaboration","Responding to change"]},' \
           '{"category":"Science: Computers","type":"multiple","difficulty":"medium","question":"What is the main CPU ' \
           'is the Sega Mega Drive \/ Sega Genesis?","correct_answer":"Motorola 68000","incorrect_answers":["Zilog ' \
           'Z80","Yamaha YM2612","Intel 8088"]},{"category":"Science: Computers","type":"multiple",' \
           '"difficulty":"medium","question":"What was the first Android version specifically optimized for ' \
           'tablets?","correct_answer":"Honeycomb","incorrect_answers":["Eclair","Froyo","Marshmellow"]},' \
           '{"category":"Science: Computers","type":"multiple","difficulty":"hard","question":"Which RAID array type ' \
           'is associated with data mirroring?","correct_answer":"RAID 1","incorrect_answers":["RAID 0","RAID 10",' \
           '"RAID 5"]},{"category":"Science: Computers","type":"multiple","difficulty":"medium","question":"Laserjet ' \
           'and inkjet printers are both examples of what type of printer?","correct_answer":"Non-impact printer",' \
           '"incorrect_answers":["Impact printer","Daisywheel printer","Dot matrix printer"]},{"category":"Science: ' \
           'Computers","type":"multiple","difficulty":"easy","question":"The C programming language was created by ' \
           'this American computer scientist. ","correct_answer":"Dennis Ritchie","incorrect_answers":["Tim Berners ' \
           'Lee","al-Khw\u0101rizm\u012b","Willis Ware"]},{"category":"Science: Computers","type":"multiple",' \
           '"difficulty":"medium","question":"Which programming language was developed by Sun Microsystems in 1995?",' \
           '"correct_answer":"Java","incorrect_answers":["Python","Solaris OS","C++"]},{"category":"Science: ' \
           'Computers","type":"multiple","difficulty":"medium","question":"The name of technology company HP stands ' \
           'for what?","correct_answer":"Hewlett-Packard","incorrect_answers":["Howard Packmann","Husker-Pollosk",' \
           '"Hellman-Pohl"]},{"category":"Science: Computers","type":"multiple","difficulty":"hard","question":"What ' \
           'is the name given to layer 4 of the Open Systems Interconnection (ISO) model?",' \
           '"correct_answer":"Transport","incorrect_answers":["Session","Data link","Network"]},{"category":"Science: ' \
           'Computers","type":"multiple","difficulty":"hard","question":"What vulnerability ranked #1 on the OWASP ' \
           'Top 10 in 2013?","correct_answer":"Injection ","incorrect_answers":["Broken Authentication","Cross-Site ' \
           'Scripting","Insecure Direct Object References"]},{"category":"Science: Computers","type":"multiple",' \
           '"difficulty":"medium","question":"Approximately how many Apple I personal computers were created?",' \
           '"correct_answer":"200","incorrect_answers":["100","500","1000"]},{"category":"Science: Computers",' \
           '"type":"multiple","difficulty":"easy","question":"Which programming language shares its name with an ' \
           'island in Indonesia?","correct_answer":"Java","incorrect_answers":["Python","C","Jakarta"]},' \
           '{"category":"Science: Computers","type":"multiple","difficulty":"medium","question":"How many bytes are ' \
           'in a single Kibibyte?","correct_answer":"1024","incorrect_answers":["2400","1000","1240"]},' \
           '{"category":"Science: Computers","type":"multiple","difficulty":"hard","question":"The acronym ' \
           '&quot;RIP&quot; stands for which of these?","correct_answer":"Routing Information Protocol",' \
           '"incorrect_answers":["Runtime Instance Processes","Regular Interval Processes","Routine Inspection ' \
           'Protocol"]},{"category":"Science: Computers","type":"multiple","difficulty":"hard","question":"What was ' \
           'the name of the first Bulgarian personal computer?","correct_answer":"IMKO-1","incorrect_answers":[' \
           '"Pravetz 82","Pravetz 8D","IZOT 1030"]},{"category":"Science: Computers","type":"multiple",' \
           '"difficulty":"medium","question":"Unix Time is defined as the number of seconds that have elapsed since ' \
           'when?","correct_answer":"Midnight, January 1, 1970","incorrect_answers":["Midnight, July 4, 1976",' \
           '"Midnight on the creator of Unix&#039;s birthday","Midnight, July 4, 1980"]},{"category":"Science: ' \
           'Computers","type":"multiple","difficulty":"hard","question":"Which of the following computer components ' \
           'can be built using only NAND gates?","correct_answer":"ALU","incorrect_answers":["CPU","RAM",' \
           '"Register"]},{"category":"Science: Computers","type":"multiple","difficulty":"easy","question":"What ' \
           'language does Node.js use?","correct_answer":"JavaScript","incorrect_answers":["Java","Java Source",' \
           '"Joomla Source Code"]}]} '
response_json = json.loads(response)


class QuizTest:
    def __init__(self, master=None):
        self._top_level = tk.Toplevel(master)
        self._top_level.title("Quiz")

        # Positioning the top level window
        window_width = self._top_level.winfo_reqwidth()
        window_height = self._top_level.winfo_reqheight()

        position_x = int(self._top_level.winfo_screenwidth() / 2 - window_width)
        position_y = int(self._top_level.winfo_screenheight() / 2 - window_height / 1.5)

        self._top_level.geometry(str(WIDTH) + "x" + str(HEIGHT) + "+" + str(position_x) + "+" + str(position_y))
        self._top_level.resizable(False, False)

        self._time_remaining = IntVar(value=DURATION)
        self._time_after_job = self._top_level.after(1000, self._decrease_time_remaining)

        self._current_accuracy = DoubleVar(value=0.0)
        self._total_questions = 0
        self._right_questions = 0

        self._current_question = StringVar(value='N/A')
        self._current_question_index = 0
        self._current_correct_answer = StringVar(value='N/A')

        # Creating the layout

        main_frame = ttk.Frame(self._top_level, style="Red.TFrame")
        main_frame.pack(expand=1, fill=tk.BOTH)

        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=4)
        main_frame.rowconfigure(2, weight=3)
        main_frame.columnconfigure(0, weight=1)

        stats_frame = ttk.Frame(main_frame, style='Yellow.TFrame')
        stats_frame.grid(row=0, column=0, sticky='nwes')
        stats_frame.rowconfigure(0, weight=1)
        stats_frame.columnconfigure(0, weight=1)

        labels_frame = ttk.Frame(stats_frame, style='Light.TFrame')
        labels_frame.grid(row=0, column=0, sticky='nwes')
        # Remaining time
        remaining_time_label = ttk.Label(labels_frame, text='Remaining time: ')
        remaining_time_label.pack(side=tk.LEFT, padx=10)
        remaining_time = ttk.Label(labels_frame, textvariable=self._time_remaining)
        remaining_time.pack(side=tk.LEFT, padx=(0, 20))

        # Current accuracy
        accuracy_label = ttk.Label(labels_frame, text='Accuracy: ')
        accuracy_label.pack(side=tk.LEFT, padx=10)
        accuracy = ttk.Label(labels_frame, textvariable=self._current_accuracy)
        accuracy.pack(side=tk.LEFT, padx=(0, 5))
        perc = ttk.Label(labels_frame, text='%')
        perc.pack(side=tk.LEFT)

        word_frame = ttk.Frame(main_frame, style='Red.TFrame')
        word_frame.grid(row=1, column=0, sticky='nwes')
        word_frame.rowconfigure(0, weight=1)
        word_frame.columnconfigure(0, weight=1)

        self._current_question_label = ttk.Label(word_frame, textvariable=self._current_question,
                                                 wraplength=WIDTH - WIDTH / 10)
        self._current_question_label.grid(row=0, column=0, sticky='nwes')

        buttons_frame = ttk.Frame(main_frame, style='Green.TFrame')
        buttons_frame.grid(row=2, column=0, sticky='nwes')

        # Creating buttons for answers
        self._buttons = []
        for i in range(0, 2):
            buttons_frame.rowconfigure(i, weight=1)
            for j in range(0, 2):
                buttons_frame.columnconfigure(j, weight=1)
                btn = ttk.Button(buttons_frame, text='N/A')
                btn.bind('<Button-1>', self._button_click)
                btn.grid(row=i, column=j, sticky='nwes')
                self._buttons.append(btn)

        self._new_question()

    @property
    def top_level(self):
        return self._top_level

    def _decrease_time_remaining(self):
        """
        This function decrease the remaining time.
        """
        self._time_remaining.set(self._time_remaining.get() - 1)
        self._time_after_job = self._top_level.after(1000, self._decrease_time_remaining)
        if self._time_remaining.get() <= 0:
            # If the time is over we want to restart the counter (for simplicity)
            self._time_remaining.set(DURATION)
            self._current_accuracy.set(0.0)
            self._total_questions = 0
            self._right_questions = 0
            self._new_question()

    def clear_after_jobs(self):
        self._top_level.after_cancel(self._time_after_job)

    def _new_question(self):
        """
        This function take a random question from the group of questions selected. Also, it shows it.
        """
        questions = response_json['results']
        question = questions[self._current_question_index]
        # This 'html.unescape' is mandatory to avoid display errors for the text (for example the ' is shown as ?)
        self._current_question.set(html.unescape(question['question']))
        correct_answer = html.unescape(question['correct_answer'])
        self._current_correct_answer = correct_answer
        wrong_answers = html.unescape(question['incorrect_answers'])
        answers = wrong_answers + [correct_answer]
        random.shuffle(answers)
        # Set the answers into buttons
        for i in range(len(self._buttons)):
            self._buttons[i]['text'] = answers[i]

        self._current_question_index += 1

    def _button_click(self, event):
        """
        This method handle the click on an answer button
        :param event: the click Event
        """
        choice = event.widget['text']
        if choice == self._current_correct_answer:
            self._right_questions += 1
        else:
            # Penalty! 10 seconds out
            self._time_remaining.set(self._time_remaining.get() - 10)
        self._total_questions += 1
        self._current_accuracy.set(float('% .2f' % (self._right_questions / self._total_questions * 100)))
        self._new_question()
