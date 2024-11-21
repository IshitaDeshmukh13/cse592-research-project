import random
import sys
import matplotlib.pyplot as plt
import time
import numpy as np

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


def calc_entropy(guesses, word_score):
    max_entropy = -1
    candidate_list = [word for word, score in word_score]
    
    overall_score = {word: (0,0) for word in candidate_list}

    for guess, score in word_score:
        if guess in guesses or score <= 0: # filter out all words that do not satisfy constraints
            continue

        feedback_counts = {}
        for target in candidate_list:

            feedback = tuple(get_vector_feedback(guess, target))
            feedback_counts[feedback] = feedback_counts.get(feedback, 0) + 1

        total = sum(feedback_counts.values())
        entropy = 0
        for count in feedback_counts.values():
            p = count / total
            entropy -= p * np.log2(p) if p > 0 else 0

        overall_score[guess] = (score, entropy)
    
    return overall_score



def make_guess(entropy_scores, csp_weight, entropy_weight, attempt):
    best_score = -1
    best_guess = None


    for word, (csp, entropy) in entropy_scores.items():
        if csp < 0:
            break
        score = csp*csp_weight + entropy*entropy_weight
        # TODO: find better formula for score given each score's weight and attempt
        if score > best_score:
            best_score = score
            best_guess = word
    
    return best_guess


def game(target_words, word_list):
    
    attempts = 100

    attempt = 1
    left_word_solved = False
    right_word_solved = False

    feedback_matrix1 = []
    feedback_matrix2 = []
    guesses = []
    score_ratings = []
    entropy_score_ratings = []
    best_guess = None

    # main game loop
    while attempt <= attempts:
        # user's word guess
        print(f"Attempt {attempt}/{attempts} - Enter your guess: ")
        guess = "spear" if not best_guess else best_guess
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
        vector_feedback1 = get_vector_feedback(target_words[0], target_words[0]) if left_word_solved else get_vector_feedback(guess, target_words[0])
        vector_feedback2 = get_vector_feedback(target_words[1], target_words[1]) if right_word_solved else get_vector_feedback(guess, target_words[1])

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
            entropy_score_ratings = calc_entropy(guesses, score_ratings)
            print("finding words for left...")
        else:
            score_ratings = score_word_list(word_list, guesses, feedback_matrix2)
            entropy_score_ratings = calc_entropy(guesses, score_ratings)
            print("finding words for right...")


        print("Scored words (best guesses at the top):")
        for word, (csp_score, entropy) in entropy_score_ratings.items():
            if csp_score <= 0:
                break
            print(f"{word}: {csp_score}, {entropy}")
        
        
        csp_weight = 1
        entropy_weight = 1
        
        best_guess = make_guess(entropy_score_ratings, csp_weight, entropy_weight, attempt)
        print("BEST GUESS: ", best_guess)  


        # INITIAL TESTING: (on 1000 attempts)
        # When using csp_weight = 1 and entropy_weight = 0 (not using entropy at all), avg_attempts = 6.359
        # When using csp_weight = 1 and entropy_weight = 1 (equal weightage), avg_attempts = 6.227

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
    plt.title('attempt spread')
    plt.xticks(range(0, max(x) + 1))
    plt.savefig("bar.png")

if __name__=="__main__":
    main()