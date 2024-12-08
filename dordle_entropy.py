"""Implementation of entropy approach."""

import random
import sys
import numpy as np
import time

# ANSI escape codes for colors
COLORS = {
    "green": "\033[92m",
    "yellow": "\033[93m",
    "gray": "\033[90m",
    "reset": "\033[0m",
}


# helper function to get vectorized feedback
# [0] indicates "gray letter"
# [1] indicates "yellow letter"
# [2] indicates "green letter"
def get_vector_feedback(guess, target):
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
    return "".join(feedback)


def make_guess(guessed_words, candidate_list, word_list, word_4_correct, wrong_guess_made):
    max_entropy = -1
    best_guess = None
    guess_list = candidate_list

    # If the agent satisfies the wrong guess condition
    if not wrong_guess_made and word_4_correct and len(candidate_list) >= 3:
        guess_list = word_list
        wrong_guess_made = True

    for guess in guess_list:
        if guess in guessed_words:
            continue

        feedback_counts = {}
        for target in candidate_list:
            # feedback mimics the response you'd receive in a game of Wordle
            # converts to tuple to use as keys in a dictionary
            feedback = tuple(get_vector_feedback(guess, target))
            # get(key, default)
            feedback_counts[feedback] = feedback_counts.get(feedback, 0) + 1

        total = sum(feedback_counts.values())
        entropy = 0
        for count in feedback_counts.values():
            p = count / total
            entropy -= p * np.log2(p) if p > 0 else 0

        if entropy > max_entropy:
            max_entropy = entropy
            best_guess = guess

    return best_guess, wrong_guess_made


def update(
    guess,
    vector_feedback1,
    guessed_words,
    candidate_list,
    correct_letters,
    possible_letters,
):
    # add guess to guessed_words set
    guessed_words.add(guess)

    # update conditions based on guess
    for i, result in enumerate(vector_feedback1):
        if result == 0:  # gray
            [
                possible_letters[j].remove(guess[i])
                for j in range(5)
                if guess[i] in possible_letters[j]
            ]
        elif result == 1:  # yellow
            if guess[i] in possible_letters[i]:
                possible_letters[i].remove(guess[i])
            correct_letters.add(guess[i])
        else:  # green
            possible_letters[i] = set(guess[i])
            correct_letters.add(guess[i])

    new_candidate_list = []
    # eliminate words that don't meet conditions
    for word in candidate_list:
        possible_candidate = True
        # if a letter is not possible in that position
        for i, letter in enumerate(word):
            if letter not in possible_letters[i]:
                possible_candidate = False
                break
        if not correct_letters.issubset(set(word)):
            possible_candidate = False
        if word in guessed_words:
            possible_candidate = False
        if possible_candidate:
            new_candidate_list.append(word)
    # Need to update the list in place
    candidate_list.clear()
    candidate_list.extend(new_candidate_list)


def game(target_words, word_list):

    attempts = 100

    attempt = 1
    left_word_solved = False
    right_word_solved = False
    left_word_wrong_guess_made = False
    right_word_wrong_guess_made = False
    left_word_4_correct = False
    right_word_4_correct = False

    # initialize agent
    candidate_list_left = word_list.copy()
    candidate_list_right = word_list.copy()

    # sort candidate_list before starting

    guessed_words_left = set()
    correct_letters_left = set()
    possible_letters_left = [set("abcdefghijklmnopqrstuvwxyz").copy() for i in range(5)]

    guessed_words_right = set()
    correct_letters_right = set()
    possible_letters_right = [
        set("abcdefghijklmnopqrstuvwxyz").copy() for i in range(5)
    ]

    # main game loop
    while attempt <= attempts:

        # guess = input(
        #     f"Attempt {attempt}/{attempts} - Enter your guess: "
        # ).lower()  # user's word guess
        # guess = make_guess(
        #     guessed_words, candidate_list, correct_letters, possible_letters
        # )
        guess = ""

        if not left_word_solved and not right_word_solved:  # priority to left word
            guess, left_word_wrong_guess_made = make_guess(guessed_words_left, candidate_list_left, word_list, left_word_4_correct, left_word_wrong_guess_made)

            # add to guessed words list
            guessed_words_left.add(guess)
            guessed_words_right.add(guess)

        elif left_word_solved and not right_word_solved:  # solve right word
            guess, right_word_wrong_guess_made = make_guess(guessed_words_right, candidate_list_right, word_list, right_word_4_correct, right_word_wrong_guess_made)

            # add to guessed words list
            guessed_words_left.add(guess)

        elif not left_word_solved and right_word_solved:  # solve left word
            guess, left_word_wrong_guess_made = make_guess(guessed_words_left, candidate_list_left, word_list, left_word_4_correct, left_word_wrong_guess_made)

            # add to guessed words list
            guessed_words_left.add(guess)

        else:
            print("ERROR 1")

        # display feedback for each target word with colored output
        colored_feedback1 = (
            get_colored_feedback(target_words[0], target_words[0])
            if left_word_solved
            else get_colored_feedback(guess, target_words[0])
        )
        colored_feedback2 = (
            get_colored_feedback(target_words[1], target_words[1])
            if right_word_solved
            else get_colored_feedback(guess, target_words[1])
        )

        # get vectorized feeback to be supplied to model
        vector_feedback1 = (
            get_vector_feedback(target_words[0], target_words[0])
            if left_word_solved
            else get_vector_feedback(guess, target_words[0])
        )
        vector_feedback2 = (
            get_vector_feedback(target_words[1], target_words[1])
            if right_word_solved
            else get_vector_feedback(guess, target_words[1])
        )

        if vector_feedback1.count(2) == 4:
            left_word_4_correct = True

        if vector_feedback2.count(2) == 4:
            right_word_4_correct = True

        if guess == target_words[0]:
            left_word_solved = True

        if guess == target_words[1]:
            right_word_solved = True

        # update based on feedback
        update(
            guess,
            vector_feedback1,
            guessed_words_left,
            candidate_list_left,
            correct_letters_left,
            possible_letters_left,
        )

        update(
            guess,
            vector_feedback2,
            guessed_words_right,
            candidate_list_right,
            correct_letters_right,
            possible_letters_right,
        )

        print(
            f"{colored_feedback1} | {colored_feedback2} --> vectorized feedback: {vector_feedback1} | {vector_feedback2}"
        )

        # check end game conditions
        if left_word_solved and right_word_solved:
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
    num_total_attempts = {}

    start_time = time.time()
    while game_num <= total_games:
        target_words = random.sample(word_list, 2)  # select two target words
        print("target words: ", target_words)
        print("*** WELCOME TO A NEW GAME OF DORDLE ***")
        game_attempt = game(target_words, word_list)
        num_attempts += game_attempt
        game_num += 1
        num_total_attempts[game_attempt] = num_total_attempts.get(game_attempt, 0) + 1
        print(num_total_attempts)

    end_time = time.time()

    print("total games", total_games)
    average = float(num_attempts / total_games)
    print(f"average attemps per game: {average}")
    print(num_total_attempts)
    print("total time: ", end_time - start_time, "seconds")


if __name__ == "__main__":
    main()
