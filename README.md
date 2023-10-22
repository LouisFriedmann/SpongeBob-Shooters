# SpongeBob-Shooters

SpongeBob-Shooters is a 2-player local multiplayer game to be played on 2 separate computers on the same WiFi. This game is inspired by the popular cartoon SpongeBob, as it 
uses the SpongeBob background, along with images and sound effects of characters such as SpongeBob, Patrick, and the Flying Dutchman. The goal of the game is for SpongeBob and 
Patrick, one played by player 1 and the other played by player 2, to shoot down the Flying Dutchman's ship which moves randomly above them. However, SpongeBob and Patrick have to jump
across platforms if they want to get closer to the Flying Dutchman. While doing this, they may fall and lose a life, or get hit by one of the random weapons the Flying Dutchman shoots
at them and lose health or a life. They each have a total of 5 lives. It will take them 25 shots to kill the boss.

Boss' weapons: Missiles (50% chance of being shot each time Flying Dutchman shoots) that go straight down, boomerangs that can bounce off of the boundaries of the game (30% chance of being 
shot each time Flying Dutchman shoots), and bombs that go straight down and deal the most damage and cover the most area (20% chance of being shot each time Flying Dutchman shoots).

Controls for each player: To jump, press up arrow. To move left and right, use left and right arrow keys. To shoot, press space (note: there's a small shooting cooldown timer per shot)

To run this: Get 2 separate computers on the same WiFi (both preferably Windows for this to work smoothly). On both computers: have Python 3 or greater installed, place all of the files in this repository in the same directory by downloading a zip file containing all files in this repository and extracting the zip file to the same directory, install the package "pygame." Also on both computers: in "network.py": on line 13, replace what's inside the quotes with your local IP Address, and in line 14 replace Enter an open port with one of your ports that is open. In "server.py", do the same thing but make sure the port number matches the port number in "network.py".  On one computer, run the "server.py" through the command prompt or through an IDE. Then, do the same for "client.py" and on the second computer, just run "client.py".
