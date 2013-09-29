import getpass
import sys
import re

from datetime import datetime, timedelta
from optparse import OptionParser
from github import Github
from github.Repository import Repository
from github.GithubException import GithubException

repository = "html5rocks/www.html5rocks.com"

def ParseIssues(issues, closed_issues):
    """
    Parses all the issues attached to the repository and determines the articles that are due
    and those that are overdue
    """
    today = datetime.today()
    late_articles = []
    due_articles = []
    unassigned = []
    completed_articles = []
 
    combined_issues = []
    [combined_issues.append(i) for i in issues]
    [combined_issues.append(i) for i in closed_issues]

    for issue in combined_issues:
        due_on_re = re.search("(due on|due):\s*(\d{4}-\d{2}-\d{2})", issue.body, flags=re.I)
        
        if due_on_re is None:
            if issue.closed_at is None:
                unassigned.append(issue)
            continue
        else:
            if issue.closed_at is not None:
                continue

        due_on = datetime.strptime(due_on_re.group(2), "%Y-%m-%d")
        issue.due_on = due_on

        if issue.closed_at is not None and (today - issue.closed_at).days < 7:
            completed_articles.append(issue) 
        
        if due_on < today:
            late_articles.append(issue)

        if (due_on - today).days < 7 and (due_on - today).days >= 0:
            due_articles.append(issue)

    return (completed_articles, late_articles, due_articles, unassigned)

def main():
    username = raw_input("Username: ")
    password = getpass.getpass() 

    g = Github(username, password)

    repo = g.get_repo(repository)
   
    label = repo.get_label("new article")

    issues = repo.get_issues(state="open", labels = [label])
    closed_issues = repo.get_issues(state="closed", labels = [label])

    today = datetime.today()

    print "Parsing Issues"
    completed_articles, late_articles, due_articles, unassigned_articles = ParseIssues(issues, closed_issues)

    print "\n\nHTML5 Rocks Weekly Report for %s" % today.date()
    print "========================================\n"

    print "Articles Delivered this week"
    print "----------------------------\n"

    if len(completed_articles) == 0:
        print "There were no articles delivered this week\n"
 
    for article in completed_articles:
        print "%s completd '%s' on  %s" % ((article.assignee or article.user).name, article.title, article.closed_at.date())
    
    print "Overdue articles"
    print "----------------\n"

    if len(late_articles) == 0:
        print "Excellent! there are no overdue articles\n"
    
    for article in late_articles:
        print "%s - '%s' was due on %s" % ((article.assignee or article.user).name, article.title, article.due_on.date())


    print "\nArticles due this week"    
    print "----------------------\n"

    if len(due_articles) == 0:    
        print "There are no articles due this week, either all is good, or someone messed up!\n"

    for article in due_articles:
        print "%s - '%s' is due on %s" % ((article.assignee or article.user).name, article.title, article.due_on.date())
   
    print "\nArticles without a due date"
    print "---------------------------\n"

    if len(unassigned_articles) == 0:
        print "All articles have been asigned, have a cocktail!\n"

    for article in unassigned_articles:
        print "%s - '%s' %s" % ((article.assignee or article.user).name, article.title, article.html_url)

   
if __name__ == "__main__":
     main()
