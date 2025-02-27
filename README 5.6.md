Word Warrior 5.6 with Al (gameserver 5.5)
Word Warrior is a tile game for spelling words on a game board.  This game uses gameserver.py on a hosted network (can be your home network) with default port 5000 routed to the server.  The wordwarrior_client.py connects up to four players and a Artificial Linguist (AL) computer player.

Word Warrior has built in spell check / dictionary and automatic score keeping.

Rev 5.3 updated (21-Feb-2025)
1. The robustness of the TCP/IP scoket connection to the server
2. Fixed a two word bug for go enable for column 0 and row 14
3. Fixed host address bug
4. Switched to socket always open strategy
5. Added retries to connect, send message, and send command
6. Added address setting fixes.
7. Added completed socket message receive with chunking

Rev 5.4-5.6 (25-Feb-2025)
1. Changed update period to 3s for game data to the server freeing up pygame window processing time (less drag on tile movement)
2. Optomized networking.

Word Warrior is open source and not copyrigthed.
Boulder Creek Video Games gameserver is copyrigthed all rights reserved.

Boulder Creek Video Games (BCVG)
Word Warrior: Freeware released under the GPL 3.0
BCVG claims tradmark on this game.
This game client is for education purposes only.
No money is made on the use of the video game client.
Contact totorodad@gmail.com

Project start: Oct-2024
Project complete: <never lol>14-Jan-2025

Unzip with 7-zip gameserver and run.  The default port is 5000.  To change the port use gameserver_3.0 -port xxxx

Unzip with 7-zip the assets folder and the word_warrior client and run the word_warrior executable or python.

If running the python this requires pygame be installed (pip install pygame)

Up to four players can log in and play on the server.  AL the computer player can be invited at any time to play as the n+1 player.

Jim