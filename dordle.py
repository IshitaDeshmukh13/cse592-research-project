import random
import sys
import matplotlib.pyplot as plt
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


def score_word_list(word_list, guesses, feedback_matrix):
    # print("guesses: ", guesses)
    # print("feedback: ", feedback_matrix)

    # initialize a dictionary to store scores for each word
    word_scores = {word: 0 for word in word_list}

    # hyper parameters
    correct_position_match_reward = 10
    correct_letter_contains_reward = 5
    incorrect_letter_penalty = -100
    uncommon_letter_penalty = -0.5
    
    # loop through each word in the word list to calculate a score
    for sample_word in word_list:
        word_score = 0
        for guess, feedback in zip(guesses, feedback_matrix):
            if guess == sample_word:
                word_score += incorrect_letter_penalty
            else:
                for i, (guess_letter, guess_fb) in enumerate(zip(guess, feedback)):   
                    if guess_fb == 2:  # guess letter is in the correct position of target word
                        if sample_word[i] == guess_letter:
                            word_score += correct_position_match_reward  # high score for a correct-position match
                        else:
                            word_score += incorrect_letter_penalty  # incorrect word
                    elif guess_fb == 1:  # guess letter is in the target word but in the wrong position
                        if guess_letter in sample_word and sample_word[i] != guess_letter:
                            word_score += correct_letter_contains_reward  # small boost for correct letter, wrong position
                        else:
                            word_score += incorrect_letter_penalty # incorrect word
                    elif guess_fb == 0:  # guess letter is not in the target word
                        if guess_letter in sample_word:
                            word_score += incorrect_letter_penalty  # incorrect word
        

        for uncommon in ['q', 'j', 'z', 'x', 'v', 'k', 'w']:
            if uncommon in sample_word:
                word_score += uncommon_letter_penalty # slight penalty if word has uncommon letters in it

        word_scores[sample_word] = word_score  # assign the computed score to the word

    # sort words by score in descending order
    sorted_words = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_words 



def game(target_words, word_list):
    
    attempts = 100

    attempt = 1
    left_word_solved = False
    right_word_solved = False

    feedback_matrix1 = []
    feedback_matrix2 = []
    guesses = []
    score_ratings = []

    # main game loop
    while attempt <= attempts:
        # user's word guess
        print(f"Attempt {attempt}/{attempts} - Enter your guess: ")
        guess = "spear" if len(score_ratings) == 0 else score_ratings[0][0]
        if len(score_ratings) > 0:
            print("Guess is: ", guess) 
        
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

        if guess == target_words[0]:
            left_word_solved = True
        
        if guess == target_words[1]:
            right_word_solved = True

        print(f"{colored_feedback1} | {colored_feedback2} --> vectorized feedback: {vector_feedback1} | {vector_feedback2}")

        # check end game conditions
        if left_word_solved and right_word_solved:
            print(f"Congratulations! You guessed both words, in {attempt} attempts!\n")
            break
        
        # kill game if on last attempt
        if attempt == attempts:
            print("Game over! Better luck next time.")
            print(f"The words were: {target_words}\n")
            break

        guesses.append(guess)
        feedback_matrix1.append(vector_feedback1)
        feedback_matrix2.append(vector_feedback2)

        if not left_word_solved:
            score_ratings = score_word_list(word_list, guesses, feedback_matrix1)
            # print("finding words for left...")
        else:
            score_ratings = score_word_list(word_list, guesses, feedback_matrix2)
            # print("finding words for right...")

        # print("Scored words (best guesses at the top):")
        # for word, score in score_ratings[:10]:
        #     print(f"{word}: {score}")


        attempt += 1

    return attempt


def preprocess_data(filename):
    with open(filename, "r") as file:
        word_list = [line.strip().lower() for line in file]
    return word_list

def main():

    total_games = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    # read word list from file
    filename = "words.txt"
    word_list = preprocess_data(filename)
    
    game_num = 1
    num_attempts = 0

    attempt_dict = {}

    start = time.time()
    while game_num <= total_games:
        target_words = random.sample(word_list, 2)  # select two target words
        print("target words: ", target_words)
        print("*** WELCOME TO A NEW GAME OF DORDLE ***")
        game_attempts = game(target_words, word_list)
        num_attempts += game_attempts
        game_num += 1

        attempt_dict[game_attempts] = attempt_dict.get(game_attempts, 0) + 1
    end = time.time()

    print("total games", total_games)
    average = float(num_attempts / total_games)
    print(f"average attemps per game: {average}")
    print("attempt spread: ", attempt_dict) # key is number of attempts, value is number of times program took that many attempts
    print("total time: ", end - start, "seconds")


    x = list(attempt_dict.keys())
    y = list(attempt_dict.values())
    plt.bar(x, y)
    plt.xlabel('num guesses')
    plt.ylabel('frequency')
    plt.title('csp results')
    plt.xticks(range(0, max(x) + 1))
    plt.savefig("bar_plot.png")

if __name__=="__main__":
    main()