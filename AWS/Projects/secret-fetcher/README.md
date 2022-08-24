Fetches all secretes you specify and turns them into a file that can be sourced to load all of them into environment variables



1. pipe3 install -r requirements.txt
2. python3 main.py --secret-prefix "some, some2, some3"
3. source the file named "secrets" that gets created at the end

This tool removes all the characters that Secret Manager accepts in the name of the secret 
and replaces them with "_". The characters are "/+=.@-"