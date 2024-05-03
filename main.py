import praw
import json
from datetime import datetime


def load_seen(file = "seen.txt"):
    '''
    Loads the set of seen comments from a file
    '''
    try:
        l = json.load(open(file))
        return set(l)
    except:
        return set()
    
def save_seen(seen, file = "seen.txt"):
    '''
    Saves the set of seen comments to a file
    '''
    json.dump(list(seen), open(file, "w+"))
        
def utc_to_human_readable(utc):
    '''
    Converts a UTC timestamp to a human readable format using PST

    utc: int, UTC timestamp
    '''
    
    # Convert the timestamp to a datetime object
    dt = datetime.fromtimestamp(utc)
    # Convert the datetime object to a string
    return dt.strftime("%Y-%m-%d %H:%M:%S")



def get_reddit(credentials_file = "credentials.json"):
    # Load the credentials from the json file
    with open(credentials_file) as f:
        credentials = json.load(f)
    # Create the reddit object
    reddit = praw.Reddit(client_id = credentials["client_id"],
                         client_secret = credentials["client_secret"],
                         user_agent = credentials["user_agent"],
                         username = credentials["username"],
                         password = credentials["password"])
    return reddit

def listen_for_prompt(reddit, prompt, callback, subreddit = "all"):
    '''
    Listens for a prompt and calls the callback function when a prompt is found

    reddit: praw.Reddit object
    callback: function to call when a mention is found
    '''

    while True:
        for comment in reddit.subreddit(subreddit).stream.comments():
            if prompt.lower() in comment.body.lower():
                callback(comment)
        

def print_comment(comment):
    '''
    Prints the mention to the console

    mention: praw.models.Comment object
    '''
    print(comment)

def handle_comment(comment):
    '''
    Handles the prompt by performing an activity check on the user the prompt was directed at and replying with the results

    mention: praw.models.Comment object
    '''

    if comment.id in seen:
        return
    else:
        seen.add(comment.id)

    # Get the user the prompt was directed at
    parent = comment.parent()
    user = parent.author

    # Find the first activity on the subreddit by the user
    comments = user.comments.new()
    submissions = user.submissions.new()

    sub = comment.subreddit

    # Filter the comments and submissions to only those on the same subreddit
    comments = [c for c in comments if c.subreddit == sub]
    submissions = [s for s in submissions if s.subreddit == sub]

    first_activity = min(comments + submissions, key = lambda x: x.created_utc)

    time_elapsed = comment.created_utc - first_activity.created_utc

    activity_per_day = (len(comments) + len(submissions)) / (time_elapsed / (60 * 60 * 24))

    # Reply to the comment
    message = f"{user.name} was first active in r/{sub.display_name} no later than {utc_to_human_readable(first_activity.created_utc)} [here](https://reddit.com{first_activity.permalink})." \
              f"Since then, they have made {len(comments)} comments and {len(submissions)} submissions. They have made an average of {activity_per_day:0.2f} comments and submissions per day since the earliest identified activity." \
              "\n\n_Note: Due to Reddit API limitations, the earliest activity seen by the bot might not be the actual earliest activity, but it provides an upper bound._"
    comment.reply(message)

    print(f"Replied to {comment.author.name} (reddit.com{comment.permalink})")


if __name__ == "__main__":
    seen = load_seen()
    reddit = get_reddit()
    prompt = "!activitycheck"

    try:
        listen_for_prompt(reddit, prompt, handle_comment, subreddit = "ucla")
    except KeyboardInterrupt:
        save_seen(seen)
        print("Exiting...")
        exit()
    
    except Exception as e:
        print(e)
        save_seen(seen)
        exit()

    