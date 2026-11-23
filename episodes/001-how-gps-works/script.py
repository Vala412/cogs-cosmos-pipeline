# Cogs & Cosmos — Video 1, script v2.
# Each line: (scene, beat_id, text_spoken, caption_text_or_None, pause_after_seconds)
# Spoken text spells out numbers the way the voice should say them; captions use digits.

# Music mood per scene (engine/mix.py) and the scene that gets the title sting / twist boom.
MOODS = {"mars": "drone", "mars2": "drone", "tw": "tense"}
STING = "title"
TWIST = "tw"
FORMAT = "long"

LINES = [
    # --- Cold open: labelled fiction ---
    ("mars", "log1", "Mission log, day two hundred and twelve. Mars, the year twenty-one forty.", "Mission log, day 212. Mars, the year 2140.", 0.5),
    ("mars", "blank", "Our rover's map is blank.", None, 0.4),
    ("mars", "nogps", "There's no GPS out here. No satellites overhead, quietly announcing the time.", None, 0.4),
    ("mars", "trick", "So before we drive anywhere, we have to rebuild a trick that every phone back on Earth pulls off, every second it's navigating.", None, 0.3),
    ("mars", "howit", "Here's how that trick works, and why it almost didn't.", None, 1.2),
    ("title", "title", "", None, 3.2),
    # --- Hook ---
    ("hook", "sats", "Right now, about twenty thousand kilometres above your head, a few dozen satellites are doing one simple thing: announcing the time.", "Right now, about 20,000 km above your head, a few dozen satellites are doing one simple thing: announcing the time.", 0.4),
    ("hook", "listen", "Your phone never answers them. It only listens.", None, 0.3),
    ("hook", "metres", "And from those announcements alone, it works out where you're standing, to within a few metres.", None, 0.5),
    ("hook", "drift", "But if the engineers who built this system had ignored Albert Einstein, that blue dot would drift away from you by kilometres, every single day.", None, 0.5),
    ("hook", "promise", "In the next few minutes, you'll see how a handful of clock readings from space become that blue dot, and why GPS only works because Einstein was right.", None, 1.0),
    # --- Beat 1: time becomes distance ---
    ("b1", "trick", "Let's start with a trick you already know.", None, 0.3),
    ("b1", "flash", "When you see lightning, you can count the seconds until the thunder arrives.", None, 0.3),
    ("b1", "sound", "Light reaches you almost instantly, but sound crawls along at about three hundred and forty metres a second.", "Light reaches you almost instantly, but sound crawls along at about 340 metres a second.", 0.3),
    ("b1", "km", "So every three seconds of waiting means the storm is roughly a kilometre away.", None, 0.4),
    ("b1", "same", "You've just turned time into distance. GPS does exactly the same thing, with radio waves instead of sound.", None, 0.5),
    ("b1", "orbits", "There are more than thirty working GPS satellites, spread across six orbits about twenty thousand two hundred kilometres up. Each one circles the Earth twice a day.", "There are more than 30 working GPS satellites, spread across six orbits about 20,200 km up. Each one circles the Earth twice a day.", 0.4),
    ("b1", "message", "And each one constantly broadcasts a message that says, in effect: I am satellite number twelve. This is exactly where I am. And this is exactly what time it is.", "And each one constantly broadcasts a message that says, in effect: \"I am satellite number 12. This is exactly where I am. And this is exactly what time it is.\"", 0.4),
    ("b1", "light", "Radio waves travel at the speed of light, about three hundred thousand kilometres every second.", "Radio waves travel at the speed of light, about 300,000 km every second.", 0.3),
    ("b1", "travel", "From a satellite straight overhead, the message takes about seven hundredths of a second to reach you.", "From a satellite straight overhead, the message takes about 0.07 seconds to reach you.", 0.3),
    ("b1", "compute", "Your phone compares the time stamped in the message with the moment it arrived, multiplies the difference by the speed of light, and gets a distance.", None, 0.4),
    ("b1", "idea", "That's the first big idea. GPS doesn't measure where you are. It measures how long a signal took to reach you.", None, 1.0),
    # --- Beat 2: four satellites ---
    ("b2", "one", "But one distance on its own isn't much use.", None, 0.3),
    ("b2", "station", "If a friend tells you they're exactly five kilometres from the railway station, they could be anywhere on a circle around it.", "If a friend tells you they're exactly 5 km from the railway station, they could be anywhere on a circle around it.", 0.4),
    ("b2", "sphere", "In space, it's the same idea in three dimensions. Knowing you're twenty-one thousand kilometres from one satellite puts you somewhere on a giant imaginary sphere.", "In space, it's the same idea in 3D. Knowing you're 21,000 km from one satellite puts you somewhere on a giant imaginary sphere.", 0.3),
    ("b2", "two", "A second satellite narrows that down to the circle where the two spheres meet.", None, 0.3),
    ("b2", "three", "A third cuts that circle to just two points, and one of them is usually far out in space, so your phone throws it away.", None, 0.3),
    ("b2", "trilat", "Three satellites, one location. This is called trilateration.", None, 0.6),
    ("b2", "four", "So why does your phone actually need at least four?", None, 0.5),
    ("b2", "quartz", "Because the weak link is in your pocket. The satellites carry atomic clocks. Your phone has a cheap quartz clock, the same kind as in a wristwatch.", None, 0.4),
    ("b2", "unknowns", "So your phone treats its own clock error as one more unknown. Four unknowns: east-west, north-south, up-down, and how wrong is my clock.", "So your phone treats its own clock error as one more unknown. Four unknowns: east–west, north–south, up–down, and \"how wrong is my clock?\"", 0.4),
    ("b2", "borrow", "Four unknowns need four measurements. The fourth satellite turns your phone's cheap clock into a precise one, borrowed from space.", None, 1.0),
    # --- Beat 3: clocks ---
    ("b3", "fast", "Why does the clock matter so much? Because light is ridiculously fast.", None, 0.3),
    ("b3", "ns", "In one nanosecond, a billionth of a second, light travels about thirty centimetres. Roughly the length of a ruler.", "In one nanosecond, a billionth of a second, light travels about 30 centimetres. Roughly the length of a ruler.", 0.4),
    ("b3", "us", "So a clock that's off by one microsecond, a millionth of a second, puts you about three hundred metres off. That's your front door versus the next street.", "So a clock that's off by one microsecond, a millionth of a second, puts you about 300 metres off. That's your front door versus the next street.", 0.4),
    ("b3", "atomic", "That's why every GPS satellite carries several atomic clocks. They count the vibrations of atoms, which never change, and stay accurate to within a few billionths of a second.", None, 0.4),
    ("b3", "ground", "Ground stations check those clocks, track every orbit, and upload corrections, so your phone always knows exactly where each satellite was when it spoke.", None, 0.4),
    ("b3", "five", "Put it all together and a phone can find itself to within about five metres under open sky.", "Put it all together and a phone can find itself to within about 5 metres under open sky.", 0.3),
    ("b3", "city", "Near tall buildings, signals bounce off walls and arrive late. That's why your blue dot sometimes jumps across the road in a city.", None, 0.5),
    ("b3", "problem", "But there's one more problem. And no amount of engineering could fix it, because it isn't a problem with the clocks. It's a problem with time itself.", None, 1.2),
    # --- Twist: Einstein ---
    ("tw", "years", "In nineteen oh five and nineteen fifteen, Albert Einstein showed that time doesn't tick at the same rate for everyone.", "In 1905 and 1915, Albert Einstein showed that time doesn't tick at the same rate for everyone.", 0.3),
    ("tw", "caught", "GPS satellites are caught between two of his ideas, pulling in opposite directions.", None, 0.4),
    ("tw", "sr", "First, special relativity: moving clocks run slow.", None, 0.3),
    ("tw", "speed", "GPS satellites race around the Earth at nearly four kilometres every second. At that speed, their clocks fall behind clocks on the ground by about seven microseconds a day.", "GPS satellites race around the Earth at nearly 4 km every second. At that speed, their clocks fall behind clocks on the ground by about 7 microseconds a day.", 0.4),
    ("tw", "gr", "Second, general relativity: gravity slows time. The deeper you sit in a gravity well, the slower your clock ticks.", None, 0.3),
    ("tw", "high", "The satellites sit far higher in Earth's well than you do, so their clocks run faster, by about forty-five microseconds a day.", "The satellites sit far higher in Earth's well than you do, so their clocks run faster, by about 45 microseconds a day.", 0.4),
    ("tw", "net", "Minus seven, plus forty-five. Every GPS satellite clock gains about thirty-eight microseconds a day.", "Minus 7, plus 45. Every GPS satellite clock gains about 38 microseconds a day.", 0.5),
    ("tw", "eleven", "That sounds tiny. But one microsecond is three hundred metres. Thirty-eight microseconds is more than eleven kilometres' worth of error. Every day.", "That sounds tiny. But one microsecond is 300 metres. 38 microseconds is more than 11 km worth of error. Every day.", 0.6),
    ("tw", "tune", "So engineers built Einstein into the hardware. Before launch, each satellite's clock is tuned to tick slightly slow: ten point two two nine nine nine nine nine nine five four three megahertz, instead of exactly ten point two three.", "So engineers built Einstein into the hardware. Before launch, each satellite's clock is tuned to tick slightly slow: 10.22999999543 MHz instead of exactly 10.23.", 0.4),
    ("tw", "orbit", "Once it's in orbit, relativity speeds it up to exactly the right rate, as seen from the ground.", None, 0.5),
    ("tw", "1977", "Not everyone was convinced at first. When the first GPS satellite with a caesium clock launched in nineteen seventy-seven, its relativity correction was left switched off for twenty days.", "Not everyone was convinced at first. When the first GPS satellite with a caesium clock launched in 1977, its relativity correction was left switched off for 20 days.", 0.4),
    ("tw", "proved", "Its clock drifted by just the amount Einstein's equations predicted. The correction was switched on, and it has been built into every GPS satellite since.", None, 1.2),
    # --- Answer ---
    ("ans", "doesnt", "So, how does GPS know where you are? It doesn't. Your phone works it out.", None, 0.4),
    ("ans", "recap", "It listens to at least four satellites, turns their time stamps into distances, solves for its own clock, and trusts atomic clocks that were set for Einstein before they ever left the ground.", None, 0.5),
    ("ans", "gnss", "And most phones don't only listen to GPS. They also use Europe's Galileo, Russia's Glonass, China's Bay-doe, and many add India's Navik. Different satellites, same idea: time becomes distance.", "And most phones don't only listen to GPS. They also use Europe's Galileo, Russia's GLONASS, China's BeiDou, and many add India's NavIC. Different satellites, same idea: time becomes distance.", 1.0),
    # --- Mars callback (fiction) ---
    ("mars2", "log2", "Mission log, day two hundred and thirteen.", "Mission log, day 213.", 0.4),
    ("mars2", "plan", "We've drafted a plan: put a few atomic clocks into orbit around Mars, and tune them before launch for Mars's gravity and their own speed, not Earth's.", None, 0.4),
    ("mars2", "right", "If Einstein was right on Earth, he'll be right out here too.", None, 1.2),
    # --- Outro ---
    ("outro", "like", "If this changed the way you see that little blue dot, hit the like button.", None, 0.3),
    ("outro", "sub", "Then subscribe to Cogs and Cosmos, and tap the bell icon so you never miss a new explainer. Keep exploring.",
     "Then subscribe to Cogs & Cosmos, and tap the bell icon so you never miss a new explainer. Keep exploring.", 2.6),
]

if __name__ == "__main__":
    words = sum(len(l[2].split()) for l in LINES)
    print("lines", len(LINES), "spoken words", words)
