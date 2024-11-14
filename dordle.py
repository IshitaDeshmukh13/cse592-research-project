import random
import sys

# ANSI escape codes for colors
COLORS = {
    "green": "\033[92m",   
    "yellow": "\033[93m", 
    "gray": "\033[90m",
    "reset": "\033[0m"    
}

# helper function to get vectorized feedback
# [0] indicates "gray letter"
# [1] indicates "yellow letter"
# [2] indicates "green letter"
def get_vector_feeback(guess, target):
    feedback = []
    for i, letter in enumerate(guess):
        if letter == target[i]:
            feedback.append(2)
        elif letter in target:
            feedback.append(1)
        else:
            feedback.append(0)
    return feedback


# helper function to get feedback and format with colors
def get_colored_feedback(guess, target):
    feedback = []
    for i, letter in enumerate(guess):
        if letter == target[i]:
            feedback.append(COLORS["green"] + letter + COLORS["reset"])
        elif letter in target:
            feedback.append(COLORS["yellow"] + letter + COLORS["reset"])
        else:
            feedback.append(COLORS["gray"] + letter + COLORS["reset"])
    return ''.join(feedback)


def game(target_words, word_list):
    
    attempts = 100

    attempt = 1
    left_word_solved = False

    # main game loop
    while attempt <= attempts:

        guess = input(f"Attempt {attempt}/{attempts} - Enter your guess: ").lower() # user's word guess
        
        # validate guess
        if len(guess) != 5 or guess not in word_list:
            print("Invalid guess. Try again.")
            continue
        

        # display feedback for each target word with colored output
        colored_feedback1 = get_colored_feedback(target_words[0], target_words[0]) if left_word_solved else get_colored_feedback(guess, target_words[0])
        colored_feedback2 = get_colored_feedback(guess, target_words[1])

        # get vectorized feeback to be supplied to model
        vector_feedback1 = get_vector_feeback(target_words[0], target_words[0]) if left_word_solved else get_vector_feeback(guess, target_words[0])
        vector_feedback2 = get_vector_feeback(guess, target_words[1])

        if guess == target_words[0]:
            left_word_solved = True

        print(f"{colored_feedback1} | {colored_feedback2} --> vectorized feedback: {vector_feedback1} | {vector_feedback2}")

        # check end game conditions
        if left_word_solved and guess == target_words[1]:
            print(f"Congratulations! You guessed both words, in {attempt} attempts!\n")
            break
        
        # kill game if on last attempt
        if attempt == attempts:
            print("Game over! Better luck next time.")
            print(f"The words were: {target_words}\n")
            break

        attempt += 1

    return attempt


def preprocess_data(filename):
    with open(filename, "r") as file:
        word_list = [line.strip().lower() for line in file]
    return word_list

def main():

    total_games = int(sys.argv[1]) if len(sys.argv) > 1 else 10

    # read word list from file
    filename = "words.txt"
    word_list = preprocess_data(filename)
    
    game_num = 1
    num_attempts = 0

    while game_num <= total_games:
        target_words = random.sample(word_list, 2)  # select two target words
        print("target words: ", target_words)
        print("*** WELCOME TO A NEW GAME OF DORDLE ***")
        num_attempts += game(target_words, word_list)
        game_num += 1
    
    print("total games", total_games)
    average = float(num_attempts / total_games)
    print(f"average attemps per game: {average}")

if __name__=="__main__":
    main()