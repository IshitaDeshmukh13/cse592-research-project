import random
import sys
import time

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


def check_word_against_knowledge(word, knowledge):
    for index, letter in enumerate(word):
        if letter not in knowledge[index]:
            return False
    return True

def guess_word(possible_words, knowledge):
    print(knowledge)
    updated_possibilities = []
    for word in possible_words:
        if check_word_against_knowledge(word, knowledge):
            updated_possibilities.append(word)
    possible_words = updated_possibilities
    return updated_possibilities[0]

def update_knowledge(knowledge, vector_feedback1, guess):
    for index, value in enumerate(vector_feedback1):
        if value == 0 or value == 1:
            if guess[index] in knowledge[index]:
                knowledge[index].remove(guess[index])
        else:
            knowledge[index] = [guess[index]]
    return knowledge

def game(target_words, word_list):
    
    attempts = 100

    attempt = 1
    left_word_solved = False
    right_word_solved = False

    possible_words_left = list(word_list)
    possible_words_right = list(word_list)
    vector_feedback1 = None
    vector_feedback2 = None
    knowledge_left = {} # mapping from position to possibilities
    knowledge_right = {}

    letters = 'abcdefghijklmnopqrstuvwxyz'
    for i in range(5):
        knowledge_left[i] = []
        knowledge_right[i] = []
        for letter in letters:
            knowledge_left[i].append(letter)
            knowledge_right[i].append(letter)

    # main game loop
    while attempt <= attempts:

        # guess = input(f"Attempt {attempt}/{attempts} - Enter your guess: ").lower() # user's word guess
        if not left_word_solved:
            guess = guess_word(possible_words_left, knowledge_left)
        else:
            guess = guess_word(possible_words_right, knowledge_right)
        print("Guessing:", guess)
        
        # validate guess
        if len(guess) != 5 or guess not in word_list:
            print("Invalid guess. Try again.")
            continue

        # display feedback for each target word with colored output
        colored_feedback1 = get_colored_feedback(target_words[0], target_words[0]) if left_word_solved else get_colored_feedback(guess, target_words[0])
        colored_feedback2 = get_colored_feedback(target_words[1], target_words[1]) if right_word_solved else get_colored_feedback(guess, target_words[1])

        # get vectorized feeback to be supplied to model
        vector_feedback1 = get_vector_feeback(target_words[0], target_words[0]) if left_word_solved else get_vector_feeback(guess, target_words[0])
        vector_feedback2 = get_vector_feeback(target_words[1], target_words[1]) if right_word_solved else get_vector_feeback(guess, target_words[1])

        knowledge_left = update_knowledge(knowledge_left, vector_feedback1, guess)
        knowledge_right = update_knowledge(knowledge_right, vector_feedback2, guess)

        if guess == target_words[0]:
            left_word_solved = True
        
        if guess == target_words[1]:
            right_word_solved = True

        print(f"{colored_feedback1} | {colored_feedback2} --> vectorized feedback: {vector_feedback1} | {vector_feedback2}")
        # print(f"{colored_feedback1} --> vectorized feedback: {vector_feedback1}")

        # check end game conditions
        if left_word_solved and right_word_solved:
            print(f"Congratulations! You guessed the word, in {attempt} attempts!\n")
            break
        
        # kill game if on last attempt
        if attempt == attempts:
            print("Game over! Better luck next time.")
            print(f"The word was: {target_words}\n")
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

    guess_distribution = {}

    start = time.time()
    while game_num <= total_games:
        target_words = random.sample(word_list, 2)  # select two target words
        print("target word: ", target_words)
        print("*** WELCOME TO A NEW GAME OF DORDLE ***")
        game_result = game(target_words, word_list)
        num_attempts += game_result
        game_num += 1

        if game_result in guess_distribution:
            guess_distribution[game_result] += 1
        else:
            guess_distribution[game_result] = 1
    end = time.time()
    
    print("total games", total_games)
    average = float(num_attempts / total_games)
    print(f"average attemps per game: {average}")
    print(f"guess distribution: {guess_distribution}")
    print("total time: ", end - start, "seconds")

if __name__=="__main__":
    main()